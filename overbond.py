import json
import re
import sys

def stderr(pValue):
    print(pValue, file=sys.stderr)

output_obj = None

if len(sys.argv) == 1:
    stderr('ERROR: The Script expects 2 input aruguments !')
    stderr('ERROR: 1> INPUT JSON File')
    stderr('ERROR: 2> OUTPUT JSON File to be generated(Overwrites if already existing!)')
elif len(sys.argv) == 2:
    stderr('WARNING: The Script expects 2 input aruguments, Only 1 is given !')
    stderr('NOTE: The 1st argumnet is considered as INPUT JSON !')
    stderr('INFO: The Output will be printed to STDOUT')
else:
    output_obj = open(sys.argv[2],'w')

input_obj = json.loads(open(sys.argv[1],'r').read())

bond_obj_attributes = list(sorted(["id","type","tenor","yield","amount_outstanding"]))
bond_obj_attribute_alias =  {
                                "term":"tenor"
                            }

stndrz_inp_bond_attrbs = lambda pBond:{(bond_obj_attribute_alias[iBK] if iBK in bond_obj_attribute_alias else iBK):iBV for iBK, iBV in pBond.items()}
def validate_bond_attrbs(pBond):
    for iAttrbs in bond_obj_attributes:
        if iAttrbs in pBond:
            if pBond[iAttrbs] == None:
                return False 
            else:
                continue
        else:
            return False
    return True

corp_bonds = []
gov_bonds  = []
result = {"data":[]}

parse_tenore = lambda pTenore:float(re.search('[0-9\.]{1,}',pTenore).group(0))
parse_yield  = lambda pYield:float(pYield.replace('%',''))

def calculate_spread(pBond):
    closest_tenor = 0
    tie_value = 0
    return_value = None
    cYield= parse_yield(pBond['yield'])
    for iGBonds in gov_bonds:
        gYield = parse_yield(iGBonds['yield'])
        tenore = abs(parse_tenore(pBond['tenor']) - parse_tenore(iGBonds['tenor']))
        if return_value == None:
            spread_t = (cYield - gYield)*100
            spread = '{:f}'.format(spread_t).split('.')[0]
            return_value = {
                "corporate_bond_id": pBond["id"],
                "government_bond_id": iGBonds["id"],
                "spread_to_benchmark": spread + ' bps'
            }
            closest_tenor = tenore
            tie_value = iGBonds['amount_outstanding']
        else:
            if tenore == closest_tenor:
                if tie_value < iGBonds['amount_outstanding']:
                    spread_t = (cYield - gYield)*100
                    spread = '{:f}'.format(spread_t).split('.')[0]
                    tie_value = iGBonds['amount_outstanding']
                    return_value = {
                                "corporate_bond_id": pBond["id"],
                                "government_bond_id": iGBonds["id"],
                                "spread_to_benchmark": spread + ' bps'
                            }
            elif tenore < closest_tenor:
                spread_t = (cYield - gYield)*100
                spread = '{:f}'.format(spread_t).split('.')[0]
                closest_tenor = tenore
                tie_value = iGBonds['amount_outstanding']
                return_value = {
                                "corporate_bond_id": pBond["id"],
                                "government_bond_id": iGBonds["id"],
                                "spread_to_benchmark": spread + ' bps'
                            }
    return return_value

for iBonds in input_obj["data"]:
    iBond_STDs = stndrz_inp_bond_attrbs(iBonds)
    if validate_bond_attrbs(iBond_STDs):
        if iBond_STDs["type"] == 'corporate':
            corp_bonds.append(iBond_STDs)
        elif iBond_STDs["type"] == 'government':
            gov_bonds.append(iBond_STDs)
        else:
            stderr("Bonds with invalid type => " + str(iBond_STDs))
    else:
        stderr("Bonds with invalid attributes => " + str(iBond_STDs))

for iBond in corp_bonds:
    result["data"].append(calculate_spread(iBond))

if output_obj == None:
    print(json.dumps(result))
else:
    output_obj.write(json.dumps(result))
