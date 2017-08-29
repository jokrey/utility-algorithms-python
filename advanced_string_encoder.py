class AdvancedStringEncoder:
    """
    Allows for a simple data to be encoded into a String.
     Nesting this allows for infinitly complex storage structures.
          Nesting is achieved by letting complex classes encode their raw data using this utility class
             (good practise is to implement EncodableAsString interface and provide a constructor that takes an encoded String)
     Accessing the data can be done over tags. If a Tag doesn't exist, the method(get_entry) will return null.
     When switching around between versions this has to be caught, but if handled right, the remaining data is not lost.
     The resulting string can then be stored without much effort.

     NOTE: This is ENCODING, NOT ENCRYPTING
        Though the results of this method may at times be hard to read for a human, should the data be sensitive then encryption is still required.
    """

    def __init__(self, working_string:str=""):
        self.work_in_progress = working_string

    def set_encoded_string(self, working_string: str):
        self.work_in_progress = working_string

    def get_encoded_string(self):
        return self.work_in_progress

    def get_entry(self, tag:str):
        current_i = 0
        while True:
            tag_content_pair = li_decode_multiple(self.work_in_progress, current_i, 2)
            if len(tag_content_pair) != 2:
                return None
            if tag == tag_content_pair[0]:
                return tag_content_pair[1]
            current_i = self.readto_next_entry(current_i)
            if current_i == 0:
                break
        return None

    def delete_entry(self, tag:str):
        current_i=0
        while True:
            tag_content_pair = li_decode_multiple(self.work_in_progress, current_i, 2)
            if len(tag_content_pair) != 2:
                return None
            if tag_content_pair[0] == tag:
                startIndex_endIndex_of_TAG = get_startAndEndIndexOf_NextLIString(current_i, self.work_in_progress)
                startIndex_endIndex_of_CONTENT = get_startAndEndIndexOf_NextLIString(startIndex_endIndex_of_TAG[1], self.work_in_progress)
                self.work_in_progress = self.work_in_progress[:current_i] +  self.work_in_progress[startIndex_endIndex_of_CONTENT[1]:]
                return tag_content_pair[1]
            current_i = self.readto_next_entry(current_i)
            if current_i == 0:
                break
        return None

    def add_entry(self, tag:str, entry):
        if type(entry) is str:
            self.delete_entry(tag)  # just in case
            self.work_in_progress += li_encode_single(tag)+li_encode_single(entry)
        elif type(entry) is bool:
            if entry:
                self.add_entry(tag, "t")
            else:
                self.add_entry(tag, "f")
        elif type(entry) is int:
            self.add_entry(tag, str(entry))

    def readto_next_entry(self, current_i:int):
        current_i = get_startAndEndIndexOf_NextLIString(current_i, self.work_in_progress)[1]  # skip tag
        current_i = get_startAndEndIndexOf_NextLIString(current_i, self.work_in_progress)[1]  # skip content
        if current_i>=len(self.work_in_progress):
            current_i=0
        return current_i




    # data type shorts
    def get_entry_boolean(self, tag:str):
        entry = self.get_entry(tag)
        return entry!=None and entry == "t"
    def delete_entry_boolean(self, tag:str):
        entry = self.delete_entry(tag)
        return entry!=None and entry == "t"

    # int shorts
    def get_entry_int(self, tag:str):
        entry = self.get_entry(tag)
        return int(entry)
    def delete_entry_int(self, tag:str):
        entry = self.delete_entry(tag)
        return int(entry)







# LI-Encoding
# Length-Indicator based encoding
def li_encode_multiple(strs):
    toReturn = ""
    for stri in strs:
        toReturn+=li_encode_single(stri)
    return toReturn

def li_decode_all(encoded_str:str):
    return li_decode_multiple(encoded_str, 0, -1)

def li_decode_multiple(encoded_str:str, start_index:int, limit:int):
    toReturn = list()

    startIndex_endIndex_ofNextLIString = [0, start_index]
    while len(startIndex_endIndex_ofNextLIString) == 2:
        if limit > -1 and len(toReturn) >= limit:  # -1 because after while one more is added added
            break
        startIndex_endIndex_ofNextLIString = get_startAndEndIndexOf_NextLIString(startIndex_endIndex_ofNextLIString[1], encoded_str)
        if len(startIndex_endIndex_ofNextLIString) == 2:
            toReturn.append(encoded_str[startIndex_endIndex_ofNextLIString[0] : startIndex_endIndex_ofNextLIString[1]])

    return toReturn

def li_encode_single(stri:str):
    return getLengthIndicatorFor(stri)+stri

def li_decode_single(encoded_str:str):
    startIndex_endIndex_ofNextLIString = get_startAndEndIndexOf_NextLIString(0, encoded_str)
    if len(startIndex_endIndex_ofNextLIString) == 2:
        return encoded_str[startIndex_endIndex_ofNextLIString[0] : startIndex_endIndex_ofNextLIString[0]+startIndex_endIndex_ofNextLIString[1]]
    else:
        None

def getLengthIndicatorFor(stri:str):
    lengthInidcators = list()
    lengthInidcators.append(str(len(stri) + 1))  # Attention: The +1 is necessary because we are adding a pseudo random char to the beginning of the splitted char to hinder a bug, if somechooses to only save a medium sized int. (It would be interpreted as a lengthIndicator)
    while len(lengthInidcators[0]) != 1:
        lengthInidcators.insert(0, str(len(lengthInidcators[0])))
    return "".join(lengthInidcators)+getPseudoRandomHashedCharAsString(stri)

def get_startAndEndIndexOf_NextLIString(start_index:int, stri:str):
    i = start_index
    if i+1 > len(stri):
        return []
    lengthIndicator = stri[i : i+1]
    i += 1
    while True:
        lengthIndicator_asInt = getInt(lengthIndicator)
        if i+lengthIndicator_asInt > len(stri):
            return []
        eitherDataOrIndicator =  stri[i : (i+lengthIndicator_asInt)]
        ifitwasAnIndicator = getInt(eitherDataOrIndicator)
        if ifitwasAnIndicator > lengthIndicator_asInt and i+ifitwasAnIndicator <= len(stri):
            i+=lengthIndicator_asInt
            lengthIndicator=eitherDataOrIndicator
        else:
            if lengthIndicator_asInt==-1:
                return []
            else:
                return [i+1, i+lengthIndicator_asInt]  # i+1 for the pseudo random hash char

def getPseudoRandomHashedCharAsString(orig_string:str):
    possibleChars = "abcdefghijklmnopqrstuvwxyz!?()[]{}=-+*#"
    additionHashSaltThingy = 0
    for b in orig_string.encode('utf-8'):
        additionHashSaltThingy += (b & 0xFF)
    return possibleChars[(len(orig_string)+additionHashSaltThingy) % len(possibleChars)]

def getInt(stri:str):
    try:
        return int(stri)
    except(ValueError):
        return -1
