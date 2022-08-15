from papp.tool import *
from papp.model.WebData import *


if __name__ == '__main__':
    res = WebData.whereId(1).find()
    print(res)
