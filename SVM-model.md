# SVM_model

As a supervised machine learning model, a support-vector machine (SVM) uses learning algorithms to analyze data for classification and regression analysis. In other words, SVM model is commnly used to find a hyperplane, in order to segregate the two classes. The object of this SVM model is to examine the underlying effects that sentiments might have on volatility of future stock returns. To achieve our goal, we set the volatility of stock returns as dependent variables and vertorized tweets as independent variables. 

There are three steps to build a SVM model. Firstly, we need to gather data for both X and y for training and testing. Secondly, we need to vectorize the data in order to get rid of explicit for loops in our code. Afterwards, a linear SVM model could be built to train and then predit. 

## 1. Dependent variable Y: Direction of Stock Return for 30 Days

Firstly, we import the stock return data (take Fosun Pharma as an example) and generate a loop for future 30 days to get the stock return for the next 30 days. As shown below, we create columns in the "Fosun_stock_price" data frame to imply the time lag for 30 days. As as instance, if T = 10，a column called 'range_test_10_days' would appear and store the stock price ten days later. As we are going to classify the tweets into two classifications,'relative to stock returns' and 'irrelative to stock returns', therefore, the binary classification is applied below. 

```python
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn import preprocessing
from sklearn import utils  
from sklearn.metrics import classification_report
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

Fosun_stock_price = pd.read_csv("../dataset/fusun-pharma-2020-stock-price/fosun_pharma_2020.csv")

for i in range(1,31):
    range_test = pd.concat([Fosun_stock_price.iloc[i:]['Adj Close'],pd.Series([0]*i)])
    range_test = range_test.reset_index(drop=True)
    df_range = 'range_test_'+str(i)+'_days'
    Fosun_stock_price[df_range]=pd.Series(range_test)
    df_volatility = 'Volatility_'+str(i)+'_days'
    regression_SVM[df_range] = Fosun_stock_price[df_range]
    regression_SVM['df_volatility']=np.where(regression_SVM[df_range]/regression_SVM[df_range].shift(1)-1>0,1,0)
    y=regression_SVM['df_volatility']

```
In this way, the dependant variable y is realy to test. 

## 2. Independent Variable X:TFIDF Vertor for Daily Tweets
### 2.1 Combining daily tweets 
Following our tokenization process, we generated the tokenized words stored in "word_tokens" series. In order to obtain the consistent numbers of two sets of variables, we then create the a function, "regression_SVM_daily_tweets". This function combines the tweets obtained in the same day. 
```python

def regression_SVM_daily_tweets(df_data):
    Date = []
    for each in df_data['Timestamp']:
        date = each.split('T')[0]
        date = datetime.strptime(date, '%Y-%m-%d').date()
        Date.append(date)
    
    df_data['Date'] = pd.Series(Date)
    df_data['word_tokens']=[" ".join(word_tokens) for word_tokens in df_data['word_tokens']]
    df_polarity = (df_data.groupby(['Date']).apply(lambda x: pd.Series({'daily_tweets':" ".join(x['word_tokens'])}))
                    ).reset_index()
    
    return df_polarity

regression_SVM = regression_SVM_daily_tweets(data_frame)
```
### 2.2 TFIDF Vectorizer
We then create tf-idf vector on the daily tweets to get rid of explicit for loops in our code. 

```python 
for i in range(1,31):
    v=TfidfVectorizer(stop_words='english',max_df=0.9)
    X = v.fit_transform(regression_SVM['daily_tweets'])
```
Therefore, the independant variable X is realy to test in our model. 

## 3. Building SVM model 
By setting the depenpent vatiable y as classification result, we split data into 80/20 ratios and then apply SVM model to get the classifier. After applying the classifier into the test dataset, we then find the accuracy of vertorized tweets awards the volatility of stock returns. 

```python
for i in range(1,31):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,random_state = 40)
    classifier_linear=svm.SVC(kernel='linear')
    classifier_linear.fit(X_train,y_train)
    
    prediction_linear = classifier_linear.predict(X_test)
    report = classification_report(y_test,prediction_linear,output_dict = True)
    result=dict()
    result[df_range]=report['weighted avg']['precision']
    
    print(result)
```

## 3. Results 

As a conclusion, we could see that the precision reaches the peak at T=1, followed by T= 20 days and T = 27 days. In otehr words, the sentiment and return has significant correlation in  T= 1, with the highest precision of 78.62%. The result is roughly consistent with our regression results above, with only one-day lag. The possible reason would be the lack of sentiment analysis in SVM model. Our group generate sentiment analysis in both Lexicon-based approaches and SVM-based approaches. Through the precise contrasts, we belieev we could find the most accurate model to conduct sentimeny analysis.   

![90f321eb34ed472e0d1aa0597974b1f](https://user-images.githubusercontent.com/78474798/111010925-cf839080-838f-11eb-8caa-91667f1a70ac.png)















