from django.template import loader,Context
from django.http import HttpResponse

def init():
    link='0000000000'
    t = loader.get_template('base_p.html')
    c=Context({'link':link})
    return HttpResponse(t.render(c))
if __name__=='__main__':
    init()