# GPU-Amazon-Bot

The purpose of this script is to automate the purchase of Amazon products via **Buy Now** button

## Installation

First Install python 3.x or later.

once python is installed, run the following pip commands to install the required libraries

```
pip install beautifulsoup4
pip install selenium
pip install webdriver-manager
pip install twilio
```

Also intall Firefox Web browswer [here](https://www.mozilla.org/en-US/firefox/new/)

Finally add your firefox profile path on the script (Line 51). You can find the path by opening firefox and then putting `about:profiles` on the URL bar.

_Your path will be the 'Root Directory Path'_

## Usage

First make sure to have you account set up with a payment method and a default shipping address, so that it only takes one click to buy a product in amazon.
then change the values of the `Amazon credentials` section in the code with your Amazon credentials.

Lastly, set the desired porduct's link page or pages on the `urls` section

Once all is set up, run the script on a shell by typing

`python main.py`

#### Note

if you have any suggestions on the script (which is not optimized btw) or any improvements on the documentation, feel free to submit a PR.
