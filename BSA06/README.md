# Graph

## 한글 인식

## 데이터 시각화 라이브러리

## 대시보드 

<br/>

## 탐색적 자료 분석

> BSA06/BSA06_Pandas-EDA.ipynb

### 통계 기본

#### seaborn의 예시 데이터셋 가져오기

```python
팁  = seaborn.load_dataset('tips')
```

#### 수치형 + 범주형 데이터 요약

```python
팁.describe(include="all")
```

#### 범주마다 데이터 세기

```python
팁[['sex','smoker','day','time']].value_counts()
```

#### 수치형 데이터의 상관 계수 구하기

> 두 변수 X 와 Y 간의 선형 상관 관계를 계량화한 수치다. 피어슨 상관 계수는 코시-슈바르츠 부등식에 의해 +1과 -1 사이의 값을 가지며, +1은 완벽한 양의 선형 상관 관계, 0은 선형 상관 관계 없음, -1은 완벽한 음의 선형 상관 관계를 의미한다.

```python
팁.corr()
```

### 그룹별 통계

#### DF를 groupby()로 부분 DF로 나누기
```python
for 성별, 그룹 in 팁.groupby('sex'):
    print(성별)
    display(그룹.head())
```

### 통계 함수

#### .agg() 다중 통계 표시

```python
팁.groupby(['sex','time']).agg(['mean', 'std'])
```

#### 컬럼별로 통계 계산

```python
# 소수점 자리 수 지정
팁.groupby('sex').agg({'total_bill': ['mean','std'], 'tip': 'median', 'size': 'sum' }).round(2)
```

#### .agg()에 사용자 정의 함수 lambda 사용

```python
# CV(변동계수)
팁.groupby('sex')[['total_bill', 'tip']].agg(lambda x: x.std()/x.mean())
```

#### 그룹별 평균으로 결측값 대체

```python
# 결측값 확인
타이타닉.isna().sum()

# 평균으로 대체
타이타닉.groupby(['sex','class'],group_keys=False)['age'].apply(lambda x: x.fillna(x.mean()))

# 그룹별로 표준화
팁.groupby(['sex','time'],group_keys=False)['tip'].apply(lambda x: (x-x.mean())/x.std())
```

### 데이터 정렬

```python
# in ascending order by sex, in descending order by tip
팁.sort_values(by=["sex","tip"],ascending=[True, False]).head()
```

<br/>

> BSA06/BSA06_Pyspark-EDA.ipynb

### pyspark 

#### 세션 시작

```python
from pyspark.sql import SparkSession
스파크 = SparkSession.builder.appName('Dataframe').getOrCreate()
스파크.conf.set("spark.sql.execution.arrow.pyspark.enabled","true")  
```

#### 파이스파크 데이터프레임 스키마 함께 읽어오기

```python
DF스파크 = 스파크.read.option('encoding','cp949').option('header','true').csv("Employee.csv",inferSchema=True)
DF스파크.printSchema()
```

#### 스파크DF 컬럼 리스트

```python
DF스파크.columns
```

#### 특정 컬럼을 골라서 스팤DF로 가져오기

```python
DF스파크.select(['id','gender']).show()  
```

#### 컬럼을 조회

```python
DF스파크['gender']  # 데이터 프레임 아니므로 .show() xx
```

#### 모든 컬럼 데이터 타입 확인

```python
DF스파크.dtypes
```

#### 스팤DF 각 컬럼의 count, mean, min, max 계산

```python
DF스파크.describe().show()
```

#### 스팤DF

```python
### Adding columns in dataframe
DF스파크 = DF스파크.withColumn('jobtime2',DF스파크['jobtime']*2)
DF스파크.show()

### Rename the columns
DF스파크 = DF스파크.withColumnRenamed('jobtime2','jobtime3')
DF스파크.show()

### Drop the columns
DF스파크 = DF스파크.drop('jobtime3')
DF스파크.show()

## 조회
### Salary of the people less than or equal to 30000
DF스파크.filter("salary <= 30000").show()

#### where : filter랑 같은 기능
DF스파크.where("salary <= 30000").show()  

DF스파크.filter("salary <= 50000").select(['gender','jobcat']).show()

### 여러 조건 & |
DF스파크.filter((DF스파크['salary'] <= 30000) & (DF스파크['salary'] >= 25000)).show() 

### ~ not
DF스파크.filter(~(DF스파크['salary'] <= 30000)).show() 
```

### Pyspark groupby and aggregate function

```python
### groupBy 
DF스파크.groupBy('gender').count().show() 
DF스파크.groupBy('gender').mean().show()
DF스파크.groupBy('gender').mean('salary').show() # salary 평균만
DF스파크.groupBy(['gender','jobcat']).max().show()  # 임금 차이 $  성별, 직업도 영항을 준다

### agg
DF스파크.agg({'salary':'mean', 'salbegin':'min'}).show()
```

### orderBy

```python
DF스파크.orderBy("salary",ascending=False).show()
DF스파크.orderBy("educ","salary",ascending=[False,False]).show()
```
###### pandas와의 차이에 주의

### 스팤DF 복사

```python
DF복사 = DF스파크.select("*")  # 모든 변수를
```

### Pyspark built-in functions

```python
# 표준화
from pyspark.sql.functions import avg, col, stddev
평균 = DF복사.select(avg(col("salary")))
평균.show()

평균 = DF복사.select(avg(col("salary"))).first()[0]
print(평균)

표준편차 = DF복사.select(stddev(col("salary"))).first()[0]
print(표준편차)

DF복사.withColumn("salary_STD",(col("salary")-평균)/표준편차).show()  # 사용자 정의 함수
```