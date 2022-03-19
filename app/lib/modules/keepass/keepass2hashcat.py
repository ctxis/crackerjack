#!/usr/bin/python


# Python port of keepass2john from the John the Ripper suite (http://www.openwall.com/john/)
# ./keepass2john.c was written by Dhiru Kholia <dhiru.kholia at gmail.com> in March of 2012
# ./keepass2john.c was released under the GNU General Public License
#   source keepass2john.c source code from: http://fossies.org/linux/john/src/keepass2john.c
#
# Python port by @harmj0y, GNU General Public License
#
# TODO: handle keyfiles, test file inlining for 1.X databases, database version sanity check for 1.X
#

import sys
import os
import struct
from binascii import hexlify


def process_1x_database(data, databaseName, maxInlineSize=1024):
    index = 8
    algorithm = -1

    encFlag = struct.unpack("<L", data[index:index+4])[0]
    index += 4
    if (encFlag & 2 == 2):
        # AES
        algorithm = 0
    elif (enc_flag & 8):
        # Twofish
        algorithm = 1
    else:
        print("Unsupported file encryption!")
        return

    # TODO: keyfile processing

    # TODO: database version checking
    version = hexlify(data[index:index+4])
    index += 4
    
    finalRandomseed = hexlify(data[index:index+16]).decode()
    index += 16

    encIV = hexlify(data[index:index+16]).decode()
    index += 16
    
    numGroups = struct.unpack("<L", data[index:index+4])[0]
    index += 4
    numEntries = struct.unpack("<L", data[index:index+4])[0]
    index += 4

    contentsHash = hexlify(data[index:index+32]).decode()
    index += 32

    transfRandomseed = hexlify(data[index:index+32]).decode()
    index += 32

    keyTransfRounds = struct.unpack("<L", data[index:index+4])[0]

    filesize = len(data)
    datasize = filesize - 124

    if((filesize + datasize) < maxInlineSize):
        dataBuffer = hexlify(data[124:])
        end = "*1*%ld*%s" %(datasize, hexlify(dataBuffer))
    else:
        end = "0*%s" %(databaseName)

    return "$keepass$*1*%s*%s*%s*%s*%s*%s*%s" %(keyTransfRounds, algorithm, finalRandomseed, transfRandomseed, encIV, contentsHash, end)


def process_2x_database(data, databaseName):

    index = 12
    endReached = False
    masterSeed = ''
    transformSeed = ''
    transformRounds = 0
    initializationVectors = ''
    expectedStartBytes = ''

    while endReached == False:

        btFieldID = data[index]
        index += 1
        uSize = struct.unpack("H", data[index:index+2])[0]
        index += 2
        print ("btFieldID : %s , uSize : %s" %(btFieldID, uSize))
        
        if btFieldID == 0:
            endReached = True

        if btFieldID == 4:
            masterSeed = hexlify(data[index:index+uSize]).decode()

        if btFieldID == 5:
            transformSeed = hexlify(data[index:index+uSize]).decode()

        if btFieldID == 6:
            transformRounds = struct.unpack("H", data[index:index+2])[0]

        if btFieldID == 7:
            initializationVectors = hexlify(data[index:index+uSize]).decode()

        if btFieldID == 9:
            expectedStartBytes = hexlify(data[index:index+uSize]).decode()


        index += uSize

    dataStartOffset = index
    firstEncryptedBytes = hexlify(data[index:index+32]).decode()

    return "$keepass$*2*%s*%s*%s*%s*%s*%s*%s" %(transformRounds, dataStartOffset, masterSeed, transformSeed, initializationVectors, expectedStartBytes, firstEncryptedBytes)


def process_database(filename):

    f = open(filename, 'rb')
    data = f.read()
    f.close()

    base = os.path.basename(filename)
    databaseName = os.path.splitext(base)[0]

    fileSignature = hexlify(data[0:8])

    if(fileSignature == b'03d9a29a67fb4bb5'):
        # "2.X"
        print(process_2x_database(data, databaseName))

    elif(fileSignature == b'03d9a29a66fb4bb5'):
        # "2.X pre release"
        print(process_2x_database(data, databaseName))

    elif(fileSignature == b'03d9a29a65fb4bb5'):
        # "1.X"
        print(process_1x_database(data, databaseName))
    else:
        print("ERROR: KeePass signaure unrecognized")


# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         sys.stderr.write("Usage: %s <kdb[x] file[s]>\n" % sys.argv[0])
#         sys.exit(-1)

#     for i in range(1, len(sys.argv)):
#         process_database(sys.argv[i])
