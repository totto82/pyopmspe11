-- Copyright (C) 2023 NORCE
----------------------------------------------------------------------------
RUNSPEC
----------------------------------------------------------------------------
DIMENS 
${dic['noCells'][0]} ${dic['noCells'][1]} ${dic['noCells'][2]} /

EQLDIMS
/

TABDIMS
${dic['noSands']} 1* ${dic['tabdims']} ${dic['tabdims']} /

OIL
GAS
CO2STORE
% if dic['model'] == 'complete':
DISGAS
DIFFUSE
% endif

METRIC

START
1 'JAN' 2025 /

WELLDIMS
${len(dic['wellijk'])} ${dic['noCells'][2]} ${len(dic['wellijk'])} ${len(dic['wellijk'])} /

UNIFIN
UNIFOUT
----------------------------------------------------------------------------
GRID
----------------------------------------------------------------------------
INIT
%if dic["grid"] == 'corner-point':
INCLUDE
'GRID.INC' /
%elif dic["grid"] == 'tensor':
INCLUDE
'DX.INC' /
DY 
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['ymy'][1]} /
INCLUDE
'DZ.INC' /
TOPS
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*0.0 /
%else:
DX 
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['dsize'][0]} /
DY 
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['dsize'][1]} /
DZ 
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['dsize'][2]} /
TOPS
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*0.0 /
%endif

INCLUDE
'PERMX.INC' /

COPY 
PERMX PERMY /
PERMX PERMZ /
/

INCLUDE
'PORO.INC' /

% if dic["version"] == "master":
BCCON 
1 1 ${dic['noCells'][0]} 1 1 1 1 Z-/
/
% endif
----------------------------------------------------------------------------
PROPS
----------------------------------------------------------------------------
INCLUDE
'TABLES.INC' /

% if dic['model'] == 'complete':
DIFFC
18.01528 44.01 ${dic["diffusion"][1]} 1* ${dic["diffusion"][0]}  /
% endif
----------------------------------------------------------------------------
REGIONS
----------------------------------------------------------------------------
INCLUDE
'SATNUM.INC' /
INCLUDE
'FIPNUM.INC' /
----------------------------------------------------------------------------
SOLUTION
---------------------------------------------------------------------------
EQUIL
 0 ${dic['pressure']/1.E5} ${dic['dims'][2]} 0 0 0 1 1 0 /

RPTRST
% if dic['model'] == 'immiscible': 
 'BASIC=2' FLOWS FLORES DEN/
% else:
 'BASIC=2' DEN KRG/
%endif

% if dic['model'] == 'complete':
RSVD
0   0.0
${dic['dims'][2]} 0.0 /

RVVD
0   0.0
${dic['dims'][2]} 0.0 /

RTEMPVD
0   ${dic["temperature"][1]}
${dic['dims'][2]} ${dic["temperature"][0]} /
% endif

% if dic["version"] == "release":
BC 
1 ${dic['noCells'][0]} 1 1 1 1 Z- FREE /
/
% endif
----------------------------------------------------------------------------
SUMMARY
----------------------------------------------------------------------------
PERFORMA
FGIP
FGIR
FGIT
WBHP
/
WGIR
/
WGIT
/
----------------------------------------------------------------------------
SCHEDULE
----------------------------------------------------------------------------
RPTRST
% if dic['model'] == 'immiscible': 
 'BASIC=2' FLOWS FLORES DEN/
% else:
 'BASIC=2' DEN KRG/
%endif

WELSPECS
% for i in range(len(dic['wellijk'])):
	'INJ${i}'	'G1'	${dic['wellijk'][i][0]}	${dic['wellijk'][i][1]}	1*	'GAS' ${dic['radius'][i]}/
% endfor
/
COMPDAT
% for i in range(len(dic['wellijk'])):
	'INJ${i}'	${dic['wellijk'][i][0]}	${dic['wellijk'][i][1]}	${dic['wellijk'][i][2]}	${dic['wellijk'][i][2]}	'OPEN'	1*	1*	${2.*dic['radius'][i]} /
% endfor
/
% if dic["version"] == "master":
BCPROP
 1 'FREE' /
/
% endif

% for j in range(len(dic['inj'])):
TUNING
1e-2 ${dic['inj'][j][2] / 86400.} 1e-10 2* 1e-12/
/
/
WCONINJE
% for i in range(len(dic['wellijk'])):
% if dic['inj'][j][3+3*i] > 0:
'INJ${i}' 'GAS' ${'OPEN' if dic['inj'][j][4+3*i] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][4+3*i] * 86400 / 1.86843 : E}"}  1* 400/
% else:
'INJ${i}' 'OIL' ${'OPEN' if dic['inj'][j][4+3*i] > 0 else 'SHUT'} 
'RATE' ${f"{dic['inj'][j][4+3*i] * 86400 / 998.108 : E}"}  1* 400/
%endif
% endfor
/
TSTEP
${round(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1] / 86400.}
/
% endfor