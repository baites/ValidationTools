setenv VTOOLS_ROOT ${PWD}

setenv PATH ${PATH}:$VTOOLS_ROOT/bin

setenv PYTHONPATH $VTOOLS_ROOT/src/python

setenv ROOTSYS /afs/cern.ch/cms/sw/slc4_ia32_gcc345/lcg/root/5.18.00a-cms3 

setenv PATH ${PATH}:$ROOTSYS/bin

if ($?LD_LIBRARY_PATH) then
  setenv LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:$ROOTSYS/lib
else
  setenv LD_LIBRARY_PATH $ROOTSYS/lib
endif
