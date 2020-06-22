# [Hologram-WebApplication](https://hologram-iot-service.github.io/Hologram-WebApplication/)

### With the combination of hologram, IoT technology and chatbot. But focusing on visualization.

---

## Goal
> - Make user's life convenient
> - make user's life convenient
> - Lighting on/off is possible through the web.
> - feel as if chatting with a friend secretary
---

## Framework : Python Flask , Bootstrap

---
## Function
> -  **Weather**
> - **Light Turn on/off, Color Control**
> - **Recommend Music** 
> - **Elsa Dancing , Display on/off**

---

## Dialogflow API
The chatbot was implemented by linking the crawling weather result value with the Dialogflow API.
If you ask about the weather through chatting, the weather screen will be updated accordingly.

---

## Example Code
- Detect intent_texts ( Call Dialogflow )

```python
def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)
        return response.query_result.fulfillment_text
```

- Create Webhook  ( Send Dialogflow )
```python
# create a route for webhook
@main.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # return response
    implicit()
    return make_response(jsonify({'fulfillmentText':results('dialog')}))
```
## How to Use
1. Create your own dialogflow account.
2. import the intent.zip into the dialogflow.
3. Run it on your server.

## WEB Screen
![demo1](https://user-images.githubusercontent.com/32683894/80311610-9ac02680-881b-11ea-9589-f9a089e1a091.jpg)


## Image of Chatting System
![image](https://user-images.githubusercontent.com/32683894/81505332-61aea880-9329-11ea-8922-ba59ab74bad7.png)


# License
```xml
Copyright 2020 chlgpdus921 (Hye-Yeon Choi)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
