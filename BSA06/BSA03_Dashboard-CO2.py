#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import panel as pn
import hvplot.pandas


pn.extension("tablulator",css_files=[pn.io.resources.CSS_URLS['font-awesome']])

df = pd.read_csv("owid-co2-data.csv")


# ## 대시보드(Dashboard) 만들기
# 
# ### 형태
# 연도에 따라 이산화탄소(CO2) 총배출량과 1인당 이산화탄소 배출량 관련 정보를 보여 줌
# 
# 
# ### 출력 콘텐츠
# - 연도에 따른 대륙별 이산화탄소 총배출량과 1인당 배출량 추이
# - 연도에 따른 대륙별 이산화탄소 배출량 표
# - 연도에 따른 국가별 이산화탄소 1인당 배출량과 국가 GDP 관계
# - 연도에 따른 대륙별 이산화탄소 배출량의 소스 비교

# In[8]:


df.rename(columns = {'co2':'CO2','co2_per_capita':'인당CO2','country':'국가','year':'연도'},inplace=True)
df.rename(columns = {'coal_co2':'석탄','oil_co2':'석유','gas_co2':'가스'},inplace=True)


# ## Some minor data preprocessing

# In[9]:


# Fill NAs with 0s and create GDP per capita column
df = df.fillna(0)
df['인당GDP'] =  np.where(df['population'] != 0, df['gdp']/df['population'],0)


# need to wrap our dataframe with .interactive(): idf = df.interactive(), so that this dataframe becomes interactive and we can use Panel widgets on this dataframe

# In[10]:


# Make DataFrame Pipeline Interactive
idf = df.interactive()


# ## CO2 emission over time by continent
# 

# In[11]:


# Define Panel Widgets
연도스라이더  = pn.widgets.IntSlider(name = "연도 스라이더", start=1750, end=2020, step=5, value=1850)
# 연도스라이더


# In[12]:


# Radio buttons for CO2 measure
Y축_co2 = pn.widgets.RadioButtonGroup(
    name = "Y축",
    options = ["CO2", "인당CO2"],
    button_type = "success"
)


# In[13]:


대륙 = ["World", "Asia", "Oceania", "Europe", "Africa", "North America", "South America"]
Korea = ["South Korea","North Korea"]

파이프라인_co2 = (
    idf[(idf.연도 <= 연도스라이더) & (idf.국가.isin(대륙))]
    .groupby(["국가", "연도"])[Y축_co2].mean()
    .to_frame()
    .reset_index()
    .sort_values(by="연도")
    .reset_index(drop=True)
)


# In[14]:


# 파이프라인_co2


# In[16]:


시계열그림_co2 = 파이프라인_co2.hvplot(x="연도",by="국가", y=Y축_co2, line_width=2, title="대륙별 CO2 배출량")
# 시계열그림_co2


# ## Table - CO2 emission over time by continent
# 

# In[23]:


표_co2 = 파이프라인_co2.pipe(pn.widgets.Tabulator,pagination="remote",page_size=10,sizing_mode="stretch_both")
# 표_co2


# ## CO2 vs GDP scatter plot
# 

# In[17]:


파이프라인_co2_vs_gdp = (
    idf[(idf.연도 == 연도스라이더) & (~(idf.국가.isin(대륙)))]
    .groupby(["국가", "연도","인당GDP"])['인당CO2'].mean()
    .to_frame()
    .reset_index()
    .sort_values(by="연도")
    .reset_index(drop=True)
)

# 파이프라인_co2_vs_gdp


# In[18]:


산점도_co2_vs_gdp = 파이프라인_co2_vs_gdp.hvplot(x="인당GDP",y="인당CO2", by="국가",
                                         size=80, kind="scatter", alpha=0.7, legend=False, height=600, width=700)
# 산점도_co2_vs_gdp 


# ## Bar chart with CO2 sources by continent

# In[20]:


Y축_co2_source = pn.widgets.RadioButtonGroup(
    name = "Y축",
    options = ["석탄", "석유", "가스"],
    button_type = "success"
)

세계제외 = ["Asia", "Oceania", "Europe", "Africa", "North America", "South America"]

파이프라인_co2_source = (
    idf[(idf.연도 == 연도스라이더) & (idf.국가.isin(세계제외))]
    .groupby(["국가", "연도"])[Y축_co2_source].sum()
    .to_frame()
    .reset_index()
    .sort_values(by="연도")
    .reset_index(drop=True)
)



# In[21]:


막대그래프_co2_source = 파이프라인_co2_source.hvplot(kind='bar', x="국가", y=Y축_co2_source, title="대륙별 CO2 배출 소스")
# 막대그래프_co2_source


# ## Templates
# https://panel.holoviz.org/user_guide/Templates.html
# 
# FastListTemplate

# In[ ]:


CO2와기후변화 ="#### 이산화탄소 (CO2)는 기후 변화의 주요 원인 중 하나이다. CO2는 인간 활동, 특히 고도의 산업화와 교통, 에너지 생산 등에 의해 많이 배출되고 있다. 이산화수소와 같은 탄소 기질 배출물이 대기중에 집중되면서 기상 이변, 바다 수위 상승, 등의 기후 변화의 원인이 되고 있다."

template = pn.template.FastListTemplate(
    title = "세계 이산화탄소 배출 대시보드(World CO2 emission dashboard)",
    sidebar=[pn.pane.Markdown("# 이산화탄소 배출과 기후변화"),
             pn.pane.Markdown(CO2와기후변화),
             pn.pane.JPG('기후변화.jpg',sizing_mode='scale_both'),
             pn.pane.Markdown("## 연도 설정"),
             연도스라이더],
    main=[pn.Row(pn.Column(Y축_co2, 시계열그림_co2.panel(width=800),margin=(0,25)),
                 표_co2.panel(width=400)),
          pn.Row(pn.Column(산점도_co2_vs_gdp.panel(width=600),margin=(0,25)),
                 pn.Column(Y축_co2_source, 막대그래프_co2_source.panel(width=600)))],
    accent_base_color="#88d8b0",
    header_background="#88d8b0",
)
             
template.servable();


# In[ ]:




