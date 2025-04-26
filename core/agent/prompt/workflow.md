## 🎯 AI Banner Generation Workflow (Function Calling + Local Tools)

### 1. Validate url sent in the prompt.
 - URL should be valid url
 - Agent (Step 1) identify if url product 
  - use browser puppeteer for crawling and getting data
  - feed data to llm to identify if its a ecommerce / catalog page
  
### 2. Generate copy text based on the inventory
  - get all the inventory data
  - get price from product page
  - get header title/ product description, theme
  - Agent (Step 2) Generate copy
    - generate copy using fetched data
    
### 3. Generate UI banner 
  - based on the copy text, theme 
  - generate banner