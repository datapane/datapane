#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# inject get_ipython mock for magic functions
try:
    get_ipython
except NameError:
    from unittest.mock import Mock
    get_ipython = Mock()
    del Mock


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
print(np, KMeans, PCA, scale)
print(df)
