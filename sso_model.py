import os
import pandas as pd
from pyomo.environ import *
from pyomo.opt import SolverStatus, TerminationCondition



SOLVER_PATH_EXE = os.path.join(os.getcwd(), 'linux_solvers', 'bonmin.exe')


def SSO_model(data, shops, months, limits):

    # define parameters from matrix
    actual_sales_units = data['SalesUnits'].values

    # construct model
    model = ConcreteModel()

    # make constraints list
    model.constraints = ConstraintList()  

    # define variables
    model.shop_factor = Var(shops, domain=PositiveReals)
    model.is_considered = Var(shops, domain=Binary)
    
    # define an objective
    def obj_rule(model):
        pred_su = []
        for (index), row in data.iterrows():
            pred_su.append(sum(data.loc[(index), shop] * model.shop_factor[shop] for shop in shops))
        return sum((pred_su-actual_sales_units)**2)
    
    # define objective
    model.obj = Objective(rule=obj_rule, sense=minimize)
    
    
    def custom_rule(model, shops):
        return (model.shop_factor[shops] <= 10000*model.is_considered[shops])
    
    model.constraints_custom = Constraint(shops, rule = custom_rule)

    # consider limit on shops
    model.constraints.add(expr = (sum(model.is_considered[shop] for shop in shops) <= limits['MAX_SHOPS']))
    

    # consider absolute diff between total of predicted SU and total of actual SU
    def abs_diff(shops):
        pred_su = []
        actual_su = []
        for (index), row in data.iterrows():
            pred_su.append(sum(data.loc[(index), shop] * model.shop_factor[shop] for shop in shops))
            actual_su.append(data.loc[(index), 'SalesUnits'])
        
        model.constraints.add(expr = (sum(pred_su) - sum(actual_su))**2 <= limits['MAX_ABS_DIFF_TOTAL']**2) 
    
    abs_diff(shops)

    
    # consider monthly limits
    def monthly_limit(shops, month):
        '''Total SalesUnit (actual and predicted) by month'''
        pred_su = []
        actual_su = []
        for (index), row in data.iterrows():
            if (index)[1] == month:
                pred_su.append(sum(data.loc[(index), shop] * model.shop_factor[shop] for shop in shops))
                actual_su.append(data.loc[(index), 'SalesUnits'])
        model.constraints.add(expr =  (sum(pred_su)/sum(actual_su)-1) <= limits['diff_monthly_sales_units'])
        
        
    # loop through months 
    for month in months:
        monthly_limit(shops, month)

    # # create solver
    optimizer = SolverFactory('bonmin', executable=SOLVER_PATH_EXE)
    output = optimizer.solve(model)

    # process results
    if output.solver.status == SolverStatus.ok and output.solver.termination_condition == TerminationCondition.optimal:
        results = pd.DataFrame(data = {'shop': [key for key in model.shop_factor],
                                'shop_factors': [value(model.shop_factor[key]) for key in model.shop_factor],
                                'is_considered': [value(model.is_considered[key]) for key in model.is_considered]
                                })
                                
        return {'status':'ok', 'data':results[results['is_considered']==1]}

    elif results.solver.termination_condition == TerminationCondition.infeasible:
        return {'status':'ng', 'data': 'Solution not found: infeasible'}

    else:
        return {'status':'other', 'data': str(output.solver)}
    
