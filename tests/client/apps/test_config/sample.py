# inject get_ipython mock for magic functions
from unittest.mock import Mock
get_ipython = Mock()
#!/usr/bin/env python
# coding: utf-8

# In[89]:


get_ipython().run_line_magic('matplotlib', 'inline')

"""Sample notebook"""
import pandas as pd
df = pd.read_csv('./Subscription%20Usage%20Data-1557751202.csv')


# In[107]:


import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale
print(df)

