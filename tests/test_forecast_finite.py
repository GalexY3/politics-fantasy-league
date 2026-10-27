import math
import pytest
from politics_fantasy.forecast import poisson_log_loss

@pytest.mark.parametrize('y,lam',[(1,float('nan')),(2,float('inf')),(True,1.0),(1.5,2.0)])
def test_nonfinite_or_noninteger_poisson_rejected(y,lam):
 with pytest.raises(ValueError):poisson_log_loss(y,lam)

def test_valid_log_loss():
 assert poisson_log_loss(2,2.0)==pytest.approx(2-2*math.log(2))
