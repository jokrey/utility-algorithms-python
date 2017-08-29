from utilities.advanced_string_encoder import AdvancedStringEncoder

encoder = AdvancedStringEncoder()
encoder.add_entry("tag1", "Whatup")
encoder.add_entry("tag2", True)
encoder.add_entry("tag3", 1234123)

encodedString = encoder.get_encoded_string()
print("encodedString: " + encodedString)


decoder = AdvancedStringEncoder(encodedString)
print("at tag1: " + decoder.get_entry("tag1"))
print("at tag2: " + str(decoder.get_entry_boolean("tag2")))
print("at tag3: " + str(decoder.get_entry_int("tag3")))