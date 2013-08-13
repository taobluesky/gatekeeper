from application.forms import *
data={
    "applicant_type":1,
    "carry_in":"on",
    "carry_out":"on","out_date":'2013-06-04',
}
f= CarryForm(data)
print unicode(f.errors)