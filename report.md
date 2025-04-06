# Julius Baer Clients Onboarding Data Challenge Report
____

## Team: DesparatelyDeepSeek

### Team members:

Qingxuan Chen, Yunfei Song, Petter Stangeland, Shubham Chowdhary

### Solution work flow

We define a 3-layer screening work flow to detect client data deficiencies.
1. We scan Core Client Information, by cross-validating shared attributes in target client_profile.json, account_form.json, and pasport.json. If there's any discrepeny detected, i.e. if any information under the same attribute in any of these files mismatches, the corresponding client is rejected. This aligns with the clarification given by Julius Baer during the workshop that the purpose of rejection is to return deficient files to the client for correction.
2. We check inconsistency in passport.json file because the MRZ code should encode the correct, in terms of both order and content, name, nationality, date of birth, and passport number information of the client. In addition, we handle the starting "prefix" characters that occur in some countries' passports, and ensure that the client is rejected if such feature does not match his/her nationally conventional format because if that's the case, such client poses fradulent risk to us.
3. We use LLM to map and populate unstructured text data from the client_description.json file following strictly the form and structure of the client_profile file to make comparison and detect any inconsistency in Financial History or Education History.


### Challenges

1. Misunderstanding the problem
For the first part of the challenge we where focusing a lot of our attention on thinking of different hypothesis in the data and in general a lot of time on feature engineering. Trying essentially to predict whether or not the client would be rejected based on features such as the liquidity ratio of their asset $\frac{\text{Illiquid AUM}}{\text{Total AUM}}$, client age, time since passport issue date etc. However, after all our logistic regression scores ended up around ~ 0.52, we realized that our problem had to be solved in a different way.

2. Finding the smallest of discrepancies between the client_description.json file and the client_profile.json file
This presented itself for specifically for client 13, Fuchs Hofer Wagner, we could not at first understand why this client was rejected, despite all his information being correct in client_profile.json, account_form.json, passport.json and seemingly client_description.json... However, after carefully analyzing every single detail in the client_description we noticed that the difference had to be EUR amounts where given as decimal number as oppsed to the integers amount given in client_profile.json. This made us realize we might have to rethink our apporach, and is what led us to the solution we eventually ended up with.

3. Computational constrain
After deciding on using and LLM API for valididating the concistency between client_description.json and client_profile.json we quickly realized the computational time it took for us to process one client would not be fast enough so that we could make predictions on the 1000 label evaluation data within the 30 min between its release and the submission deadline. The solution we found for this was to create a batching system for the processing where we combine data from 30 clients, specificially rewritten in .json format and then call the LLM API to process them simultaneously. This dramatically sped up our computational time which made our solution viable. 

### How to run

1. Firstly run `unzip.py` to unzip all the files
2. Then run `account_valid.py` to get the valid/invalid clients under `datathon_evaluation`
3. Finally run `predict.ipynb` to finish the process and predictions on test data.