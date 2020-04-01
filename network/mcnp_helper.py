# Simple, High-Level wrapper, that adds some functionality to the most basic byte stream.
#
# Useful for simple, standardized inter programming language communication. Where build in high level constructs are not available.
# Inter-programming Language entails that both sides will only be able to use the most basic, low level byte-"streams".
# Writing a number bytes is easy here. However it gets tricky when the receiver doesn't know how many bytes to except.
#       For example when transmitting a file or a complex data structur such as a string.
# Sends and reads multiple byte arrays(chunks) of completly variable length over a single established connection.
#       Apart from that some very basic(and common) data types of fixed length are also supported by the protocol.
#       (byte, byte arrays of fixed length, int16(twos_compl), int32(twos_compl), int64(twos_compl), float32(IEEE-754), float64(IEEE-754))
#            NOTE: Booleans are not supported since their implementation greatly differs between common languages.
#
# The idea is that after establishing a connection the client sends a "cause" byte, indicating what kind of complex "conversation" it would like to have.
# After that both sides have to each know exactly what kind of data the other one wants.
#
#    An Example of a typical "conversation" (usefulness of the example data in the braces is debatable ;) ):
# |           Client            |            Server            |
# |                             |    waitForNewConnection      |
# |     establishConnection     |  handleConnection(newThread) |
# |                             |         waitForCause         |
# |         sendCause           |         receiveCause         |
# |                             |          waitForInt          |
# |         sendInt x           |          receiveInt          |
# |         waitForInt          |      doOperationOnX (x*x)    |
# |         receiveInt          |         sendInt (x*x)        |
# |                             | waitForChunkOfVariableLength |
# |      closeConnection        | closeConnection(finishThread)|
#
# More complex, simultaneous, two way communication (for a example a game server may need), can also be achieved using this protocol.
#    Then both sides would have 2 simultaneous, one sided(likely too slow otherwise), conversations.
#    However that may not be fast enough. Then fixed package size, with a fixed cause at byte position 0, and fixed data sizes being send in the same chunk would be preferable.
#    This protocol may then be overkill.
#
# MCNP <=> Multi Chunk Network Protocol
import os

NULL_INDICATOR = -1

def send_cause(con, cause):
    send_fixed_chunk_int32(con, cause)

def read_cause(con):
    return recv_fixed_chunk_int32(con)



def send_fixed_chunk_int32(con, int32):
    con.sendall(int32.to_bytes(length=4, byteorder='big', signed=True))

def send_fixed_chunk_int64(con, int64):
    con.sendall(int64.to_bytes(length=8, byteorder='big', signed=True))

def send_fixed_chunk_uint8array(con, uint8array):
    con.sendall(uint8array)

def recv_fixed_chunk_int32(con):
    return int.from_bytes(con.recv(4), byteorder='big', signed=True)

def recv_fixed_chunk_int64(con):
    return int.from_bytes(con.recv(8), byteorder='big', signed=True)

def recv_fixed_chunk_uint8array(con, length):
    return con.recv(length)

def start_variable(con, length):
    send_fixed_chunk_int64(con, length)
def send_variable(con, uint8array):
    start_variable(con, len(uint8array))
    send_fixed_chunk_uint8array(con, uint8array)

def recv_variable(con):
    length = recv_fixed_chunk_int64(con)
    if length == NULL_INDICATOR:
        return None

    data = b''
    while len(data) < length:
        packet = con.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data

def send_utf8(con, str):
    send_variable(con, bytearray(str,'utf-8'))

def recv_utf8(con):
    recv = recv_variable(con)
    if recv is None:
        return None
    return recv.decode('utf-8')


def send_file(con, filepath):
    start_variable(con, os.path.getsize(filepath))
    f = open(filepath, 'rb')
    from utilities.network.send_file_backport import sendfile
    sendfile(con, f)