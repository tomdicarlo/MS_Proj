/*
 * Copyright 2002-2020 Intel Corporation.
 * 
 * This software is provided to you as Sample Source Code as defined in the accompanying
 * End User License Agreement for the Intel(R) Software Development Products ("Agreement")
 * section 1.L.
 * 
 * This software and the related documents are provided as is, with no express or implied
 * warranties, other than those that are expressly stated in the License.
 */

/*
 *  This file contains an ISA-portable PIN tool for tracing memory accesses.
 */

#include <stdio.h>
#include <map>
#include <deque>
#include <cmath>
#include "pin.H"

#define MASK 0xfffffffff000

using namespace std;

static UINT64 access_count = 0;
map<void *, bool> reaccessed_pages;
map<int, int> reuse_size_counts;
deque<void *> page_accesses;

FILE * trace;

// Print a memory read record
VOID RecordMemRead(VOID * ip, VOID * addr)
{
      access_count += 1;
      void * page = (void*) ((long int)addr & MASK);
      //fprintf(trace,"%p: W %p\n", addr,page);
      deque<void *>::iterator it = std::find (page_accesses.begin(), page_accesses.end(), page);
      if (it != page_accesses.end()) {
	      int reuse_distance = it - page_accesses.begin();
	      if (reuse_size_counts.find(reuse_distance) != reuse_size_counts.end()) {
		reuse_size_counts[reuse_distance] += 1;
	      } else {
		reuse_size_counts[reuse_distance] = 1;
	      }
	      page_accesses.erase(it);
	      reaccessed_pages[page] = true;
      }
      page_accesses.push_front(page);
      
}

// Print a memory write record
VOID RecordMemWrite(VOID * ip, VOID * addr)
{
      access_count += 1;
      void * page = (void*) ((long int)addr & MASK);
      //fprintf(trace,"%p: W %p\n", addr,page);
      deque<void *>::iterator it = std::find (page_accesses.begin(), page_accesses.end(), page);
      if (it != page_accesses.end()) {
	      int reuse_distance = it - page_accesses.begin();
	      if (reuse_size_counts.find(reuse_distance) != reuse_size_counts.end()) {
		reuse_size_counts[reuse_distance] += 1;
	      } else {
		reuse_size_counts[reuse_distance] = 1;
	      }
	      page_accesses.erase(it);
	      reaccessed_pages[page] = true;
      }
      page_accesses.push_front(page);
      

//    fprintf(trace,"%p: W %p\n", ip, addr);
}

// Is called for every instruction and instruments reads and writes
VOID Instruction(INS ins, VOID *v)
{
    // Instruments memory accesses using a predicated call, i.e.
    // the instrumentation is called iff the instruction will actually be executed.
    //
    // On the IA-32 and Intel(R) 64 architectures conditional moves and REP 
    // prefixed instructions appear as predicated instructions in Pin.
    UINT32 memOperands = INS_MemoryOperandCount(ins);

    // Iterate over each memory operand of the instruction.
    for (UINT32 memOp = 0; memOp < memOperands; memOp++)
    {
        if (INS_MemoryOperandIsRead(ins, memOp))
        {
            INS_InsertPredicatedCall(
                ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead,
                IARG_INST_PTR,
                IARG_MEMORYOP_EA, memOp,
                IARG_END);
        }
        // Note that in some architectures a single memory operand can be 
        // both read and written (for instance incl (%eax) on IA-32)
        // In that case we instrument it once for read and once for write.
        if (INS_MemoryOperandIsWritten(ins, memOp))
        {
            INS_InsertPredicatedCall(
                ins, IPOINT_BEFORE, (AFUNPTR)RecordMemWrite,
                IARG_INST_PTR,
                IARG_MEMORYOP_EA, memOp,
                IARG_END);
        }
    }
}

VOID Fini(INT32 code, VOID *v)
{
    float page_reuse_percentage = (float)reaccessed_pages.size()/(float)page_accesses.size();
    map<int, int>::iterator it;
    int cumulative_reuse_distance = 0;
    float reuse_sizes[20] = {};
    for(it = reuse_size_counts.begin(); it!=reuse_size_counts.end();it++) {
	cumulative_reuse_distance += it->first*it->second;
	for(int i=0; i<20; i++){
	  if (it->first >= pow((float)2, (float)i)) {
	     reuse_sizes[i] += it->second;
	  } else {
	    break;
	  }
	}
    }

    float avg_reuse_distance = (float)cumulative_reuse_distance/(float)access_count;


    fprintf(trace, "Total Number of Memory Accesses:%lu\n", access_count);
    fprintf(trace, "Total Number of Unique Page Uses:%lu\n", page_accesses.size());
    fprintf(trace, "Total Number of Page Reacceses:%lu\n", reaccessed_pages.size());
    fprintf(trace, "Page Reuse Percentage: %f\n", page_reuse_percentage);
    fprintf(trace, "Average Reuse Distance: %f\n", avg_reuse_distance);
    fprintf(trace, "CDFS: 0-19\n");
    for(int i=0; i<20;i++){
	float cdf = (access_count -reuse_sizes[i])/(float)access_count;
	fprintf(trace, "%f\n", cdf);
    }
    fprintf(trace, "#eof\n");
    fclose(trace);
}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */
   
INT32 Usage()
{
    PIN_ERROR( "This Pintool prints a trace of memory addresses\n" 
              + KNOB_BASE::StringKnobSummary() + "\n");
    return -1;
}

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */

int main(int argc, char *argv[])
{
    if (PIN_Init(argc, argv)) return Usage();

    trace = fopen("pinatrace.out", "w");

    INS_AddInstrumentFunction(Instruction, 0);
    PIN_AddFiniFunction(Fini, 0);

    // Never returns
    PIN_StartProgram();
    
    return 0;
}
