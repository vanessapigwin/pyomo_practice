import os, stat
from dotenv import load_dotenv
from os.path import dirname, abspath
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from preprocess import Excel_Processing as ep
from sso_model import SOLVER_PATH_EXE
from sso_model import SSO_model
from sso_form import FileForm


# load envs
path = dirname(abspath(__file__)) + '/.env'
load_dotenv(path)
# set executable file
st = os.stat(SOLVER_PATH_EXE)
os.chmod(SOLVER_PATH_EXE, st.st_mode | 0o111)


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 # 1 mb limit
Bootstrap(app)


# set limits
limits = {
    # max shops included in modeling output
    'MAX_SHOPS' : 20,
    
    # maxmimum absolute difference (predicted-actual)
    'MAX_ABS_DIFF_TOTAL' : 500,
    
    # max difference (predicted vs target) in monthly sales 
    'diff_monthly_sales_units' : 0.1,
}

@app.route('/', methods= ['GET', 'POST'])
def home():
    form = FileForm()

    if form.validate_on_submit():
        # read process solve
        f = form.file.data
        cleaned_df = ep(f)
        shops = cleaned_df.shops
        months = cleaned_df.months
        data = cleaned_df.data
        solution = SSO_model(data, shops, months, limits)

        # output a csv
        if solution['status'] == 'ok':
            # format an output table
            result_table = [solution['data'].to_html(index=False, header=True,
            classes=["table-bordered", "table-striped", "table-hover"], 
            col_space = 200, 
            justify='center')]

            return render_template('result.html', tables=result_table)
        
        else:
            return render_template('result.html', text=solution['data'])

    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
