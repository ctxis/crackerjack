import string


class HashIdentifier:
    b64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890+/='
    b64dot = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890+/=.'

    def __find(self, hash):
        if hash[0] == '$':
            matches = self.__find_hash_format_dollar(hash)
        elif self.__is_hex(hash):
            matches = self.__find_hash_format_hex(hash)
        elif ':' in hash:
            matches = self.__find_hash_format_colon(hash)
        elif '{' in hash and '}' in hash:
            matches = self.__find_hash_format_braces(hash)
        elif ',' in hash:
            matches = self.__find_hash_format_comma(hash)
        elif '$' in hash:
            matches = self.__find_hash_format_dollar_within(hash)
        elif '@' in hash:
            matches = self.__find_hash_format_at(hash)
        elif '*' in hash:
            matches = self.__find_hash_format_asterisk(hash)
        else:
            matches = self.__find_hash_format_misc(hash)

        return matches

    def __find_hash_format_dollar(self, hash):
        matches = []

        # Remove the $ from the beginning, and split by $.
        hash = hash[1:].split('$')
        subhash = list(filter(len, hash[1].split('*')))
        separators = len(hash)
        subseparators = len(subhash)

        sig = hash[0]

        if sig == 'episerver':
            if subhash[0] == '0':
                matches.append(141)
            elif subhash[0] == '1':
                matches.append(1441)
        elif sig == 'P' and self.__is_base64(True, hash[1]):
            matches.append(400)
        elif sig == 'DCC2':
            subhash = list(filter(len, hash[1].split('#')))
            if self.__is_hex(subhash[2]):
                matches.append(2100)
        elif sig == 'S' and self.__is_base64(False, hash[1]):
            matches.append(7900)
        elif sig == 'racf' and self.__is_hex(subhash[1]):
            matches.append(8500)
        elif sig == 'office':
            if subhash[0] == '2007':
                matches.append(9400)
            elif subhash[0] == '2010':
                matches.append(9500)
            elif subhash[0] == '2013':
                matches.append(9600)
            elif len(hash) > 2 and hash[1] == '2016':
                matches.append(25300)
        elif sig == 'oldoffice':
            if subhash[0] in ['0', '1']:
                if ':' in subhash[-1]:
                    matches.extend([9720])
                else:
                    matches.extend([9700, 9710])
            elif subhash[0] in ['3', '4']:
                matches.extend([9800, 9810, 9820])
        elif sig == 'pdf':
            if subhash[0] == '1':
                if ':' in subhash[-1]:
                    matches.extend([10420])
                else:
                    matches.extend([10400, 10410])
            elif subhash[0] == '2':
                matches.append(10500)
                matches.append(25400)
            elif subhash[0] == '5':
                matches.extend([10600, 10700])
        elif sig == 'postgres' and subhash[0] == 'postgres' and self.__is_hex(subhash[2]):
            matches.append(11100)
        elif sig == 'mysqlna' and self.__is_hex(subhash[1]):
            matches.append(11200)
        elif sig == '1' and self.__is_base64(True, hash[2]):
            matches.append(500)
        elif sig == 'BLAKE2' and self.__is_hex(hash[1]):
            matches.append(600)
        elif sig == 'apr1' and hash[1].isdigit() and self.__is_base64(True, hash[2]):
            matches.append(1600)
        elif sig == '6' and hash[1].isdigit() and self.__is_base64(True, hash[2]):
            matches.append(1800)
        elif sig == 'PHPS' and self.__is_hex(hash[2]):
            matches.append(2612)
        elif sig == '2a' and hash[1].isdigit() and self.__is_base64(True, hash[2]):
            matches.append(3200)
        elif sig == 'B' and self.__is_hex(hash[2]):
            matches.append(3711)
        elif sig == 'ml' and hash[1].isdigit() and self.__is_base64(True, hash[3]):
            matches.append(7100)
        elif sig == '5' and hash[1].isdigit() and self.__is_base64(True, hash[2]):
            matches.append(7400)
        elif sig == 'mysql':
            subhash = hash[2].split('*')
            if self.__is_hex(subhash[1], subhash[2]):
                matches.append(7401)
        elif sig == 'krb5pa' and self.__is_hex(hash[-1]):
            if hash[1] == '23':
                matches.append(7500)
            elif hash[1] == '17':
                matches.append(19800)
            elif hash[1] == '18':
                matches.append(19900)
        elif sig == 'fde' and len(hash[5]) > 2048 and self.__is_hex(hash[5]):
            matches.append(8800)
        elif sig == '8' and hash[1].isdigit() and self.__is_base64(True, hash[2]):
            matches.append(9200)
        elif sig == '9' and hash[1].isdigit() and self.__is_base64(True, hash[2]):
            matches.append(9300)
        elif sig == 'cram_md5' and self.__is_base64(False, hash[1], hash[2]):
            matches.append(10200)
        elif sig == 'bitcoin' and self.__is_hex(hash[2]):
            matches.append(11300)
        elif sig == 'sip' and 'MD5' in hash[1]:
            matches.append(11400)
        elif sig == '7z':
            matches.append(11600)
        elif sig == 'ecryptfs':
            matches.append(12200)
        elif sig == 'RAR3':
            if subhash[0] == '0' and self.__is_hex(subhash[1], subhash[2]):
                matches.append(12500)
            elif subhash[0] == '1':
                if subhash[3] == '16':
                    matches.extend([23700])
                elif subhash[3] == '32':
                    matches.extend([23800])
        elif sig == 'blockchain':
            if len(hash[2]) > 512 and self.__is_hex(hash[2]):
                matches.append(12700)
            elif hash[1] == 'v2':
                matches.append(15200)
        elif sig == 'rar5':
            matches.append(13000)
        elif sig == 'krb5tgs' and self.__is_hex(hash[-1]):
            if hash[1] == '23':
                matches.append(13100)
            elif hash[1] == '17':
                matches.append(19600)
            elif hash[1] == '18':
                matches.append(19700)
        elif sig == 'axcrypt':
            if subseparators == 4:
                matches.extend([13200])
            else:
                matches.extend([23500, 23600])
        elif sig == 'axcrypt_sha1' and self.__is_hex(hash[1]):
            matches.append(13300)
        elif sig == 'keepass':
            matches.append(13400)
        elif sig == 'zip2':
            matches.append(13600)
        elif sig == 'sha1' and self.__is_base64(True, hash[3]):
            matches.append(15100)
        elif sig == 'tacacs-plus' and self.__is_hex(hash[2], hash[3]):
            matches.append(16100)
        elif sig == 'fvde':
            if hash[1] == '1':
                matches.append(16700)
            elif hash[1] == '2':
                matches.append(18300)
        elif sig == 'pkzip2':
            if subhash[0] == '1' and len(subhash[-1]) < 500:
                matches.append(17200)
            elif subhash[0] == '1' and len(subhash[-1]) > 500:
                matches.append(17210)
            elif subhash[0] == '3' and len(subhash[-1]) > 400:
                matches.append(17220)
            elif subhash[0] == '3' and len(subhash[-1]) < 128:
                matches.append(17225)
            elif subhash[0] == '8':
                matches.append(17230)
        elif sig == 'krb5asrep' and hash[1] == '23' and self.__is_hex(hash[-1]):
            matches.append(18200)
        elif sig == 'pbkdf2-sha512' and self.__is_base64(True, hash[2], hash[3]):
            matches.append(20200)
        elif sig == 'pbkdf2-sha256' and self.__is_base64(True, hash[2], hash[3]):
            matches.append(20300)
        elif sig == 'pbkdf2' and self.__is_base64(True, hash[2], hash[3]):
            matches.append(20400)
        elif sig == 'SHA' and self.__is_hex(hash[-1]):
            matches.append(20711)
        elif sig == 'solarwinds':
            if hash[1] == '0':
                matches.append(21500)
            elif hash[1] == '1':
                matches.append(21501)
        elif sig == 'itunes_backup':
            if subhash[0] == '9':
                matches.append(14700)
            elif subhash[0] == '10':
                matches.append(14800)
        elif sig == 'DPAPImk':
            if subhash[3] == 'des3' and subhash[4] == 'sha1':
                matches.append(15300)
            elif subhash[3] == 'aes256' and subhash[4] == 'sha512':
                matches.append(15900)
        elif sig == 'chacha20':
            matches.append(15400)
        elif sig == 'jksprivk' and len(subhash[2]) > 2048:
            matches.append(15500)
        elif sig == 'ethereum':
            if subhash[0] == 'p':
                matches.append(15600)
            elif subhash[0] == 's':
                matches.append(15700)
            elif subhash[0] == 'w':
                matches.append(16300)
        elif sig == 'ASN':
            matches.append(16200)
        elif sig == 'electrum':
            if subhash[0] == '1':
                matches.append(16600)
            elif subhash[0] == '4':
                matches.append(21700)
            elif subhash[0] == '5':
                matches.append(21800)
        elif sig == 'ansible':
            matches.append(16900)
        elif sig == 'odf':
            if subhash[0] == '1':
                matches.append(18400)
            elif subhash[0] == '0':
                matches.append(18600)
        elif sig == 'ab':
            matches.append(18900)
        elif sig == 'diskcryptor' and len(subhash[-1]) == 4096:
            matches.extend([20011, 20012, 20013])
        elif sig == 'bitlocker' and self.__is_hex(hash[-1]):
            matches.append(22100)
        elif sig == 'telegram':
            if subhash[0] == '0':
                matches.append(22301)
            elif subhash[0] == '1':
                matches.append(22600)
            elif subhash[0] == '2':
                matches.append(24500)
        elif sig == 'aescrypt':
            matches.append(22400)
        elif sig == 'multibit':
            if subhash[0] == '1':
                matches.append(22500)
            elif subhash[0] == '2':
                matches.append(22700)
        elif sig == 'sshng' and self.__is_hex(hash[-1]):
            if hash[1] == '0':
                matches.append(22911)
            elif hash[1] == '6':
                matches.append(22921)
            elif hash[1] == '1':
                matches.append(22931)
            elif hash[1] == '4':
                matches.append(22941)
            elif hash[1] == '5':
                matches.append(22951)
        elif sig == 'zip3':
            if subhash[2] == '128':
                matches.append(23001)
            elif subhash[2] == '192':
                matches.append(23002)
            elif subhash[2] == '256':
                matches.append(23003)
        elif sig == 'keychain':
            matches.append(23100)
        elif sig == 'xmpp-scram':
            matches.append(23200)
        elif sig == 'iwork':
            matches.append(23300)
        elif sig == 'bitwarden':
            matches.append(23400)
        elif sig == 'bcve':
            matches.append(23900)
        elif sig == 'PEM':
            if hash[1] == '1':
                matches.append(24410)
            elif hash[1] == '2':
                matches.append(24420)
        elif sig == 'mongodb-scram':
            if subhash[0] == '0':
                matches.append(24100)
            elif subhash[0] == '1':
                matches.append(24200)
        elif sig == 'stellar':
            matches.append(25500)
        elif sig == 'knx-ip-secure-device-authentication-code':
            matches.append(25900)
        elif sig == 'mozilla':
            if subhash[0] == '3DES':
                matches.append(26000)
            elif subhash[0] == 'AES':
                matches.append(26100)

        return matches

    def __find_hash_format_hex(self, hash):
        matches = []

        if len(hash) == 8:
            matches.append(18700)
        elif len(hash) == 16:
            matches.extend([200, 3000, 5100])
        elif len(hash) == 24:
            matches.extend([20500, 20510])
        elif len(hash) == 32:
            matches.extend([0, 900, 1000, 2600, 4300, 4400, 8600, 9900, 20900])
        elif len(hash) == 40:
            matches.extend([100, 300, 4500, 4700, 6000, 18500])
        elif len(hash) == 48:
            matches.append(122)
        elif len(hash) == 50:
            matches.append(125)
        elif len(hash) == 56:
            matches.extend([1300, 17300, 17700])
        elif len(hash) == 64:
            matches.extend([1400, 6900, 11700, 17400, 17800, 20800, 21400])
        elif len(hash) == 70:
            matches.append(1421)
        elif len(hash) == 96:
            matches.extend([10800, 17500, 17900])
        elif len(hash) == 128:
            matches.extend([1700, 6100, 11800, 17600, 18000, 21000])
        elif len(hash) >= 1024:
            matches.extend([6211, 6212, 6213, 6221, 6222, 6223, 6231, 6232, 6233, 6241, 6242, 6243])
            matches.extend([13711, 13712, 13713, 13721, 13722, 13723, 13731, 13732, 13733])
            matches.extend([13741, 13742, 13743, 13751, 13752, 13753, 13761, 13762, 13763, 13771, 13772, 13773])
        elif len(hash) >= 512:
            if len(hash) == 786:
                matches.extend([2500, 2501])
            else:
                matches.extend([5200])
        elif len(hash) > 128:
            matches.extend([1722, 9000, 12300, 12900, 22200])
        else:
            matches.extend([8100, 24700])

        return matches

    def __find_hash_format_colon(self, hash):
        matches = []

        hash = list(filter(len, hash.split(':')))
        separators = len(hash)
        if separators == 2:
            if hash[0].isdigit():
                if hash[1] == '3600':
                    matches.extend([18100])
                else:
                    matches.extend([7300])
            elif self.__is_hex(hash[0]):
                if len(hash[0]) <= 16:
                    if len(hash[0]) == 8 and len(hash[0]) == 8:
                        if hash[1] == '00000000':
                            matches.extend([11500])
                        else:
                            matches.extend([14900])
                    else:
                        matches.extend([3100, 14000, 14100])
                elif len(hash[0]) == 32:
                    matches.extend([10, 11, 12, 20, 21, 23, 24, 30, 40, 50, 60, 1100, 2611, 2711, 2811, 3710, 3800, 3910])
                    matches.extend([4010, 4110, 11000, 21200, 21300])
                elif len(hash[0]) == 40:
                    matches.extend([110, 112, 120, 121, 130, 140, 150, 160, 4510, 4520, 4521, 4522, 4710, 4711, 4900])
                    matches.extend([5800, 8400,  13500, 13900, 14400, 21100, 24300])
                elif len(hash[0]) == 64:
                    matches.extend([1410, 1420, 1430, 1440, 1450, 1460, 11750, 11760, 12600, 13800, 20710, 22300])
                elif len(hash[0]) == 128:
                    matches.extend([1710, 1720, 1730, 1740, 1750, 1760, 11850, 11860, 15000])
            elif self.__is_base64(True, hash[0]):
                matches.extend([22, 2410])
        elif separators == 3:
            if self.__is_hex(hash[0]):
                matches.extend([4800, 6600, 6800, 16801, 19300, 19500])
        elif separators == 4:
            if hash[0] == 'sha256':
                matches.extend([10900])
            elif hash[0] == 'md5':
                matches.extend([11900])
            elif hash[0] == 'sha1':
                matches.extend([12000])
            elif hash[0] == 'sha512':
                matches.extend([12100])
            elif hash[0] == 'otm_sha256':
                matches.extend([20600])
            elif self.__is_hex(hash[0]):
                matches.extend([8200, 10100, 16800])
            elif self.__is_base64(hash[0]):
                matches.extend([5500, 8300])
        elif separators == 5:
            if self.__is_base64(hash[0]):
                matches.extend([5600])
        elif separators == 6:
            if hash[0] == 'SCRYPT':
                matches.extend([8900])
        elif separators == 9:
            if self.__is_hex(hash[0]):
                matches.extend([5300, 5400])

        return matches

    def __find_hash_format_braces(self, hash):
        matches = []

        sig, data = self.__extract_braces(hash)
        if sig == '{SHA}':
            matches.extend([101])
        elif sig == '{SSHA}':
            matches.extend([111])
        elif sig == '{SSHA256}':
            matches.extend([1411])
        elif sig == '{SSHA512}':
            matches.extend([1711])
        elif sig == '{smd5}':
            matches.extend([6300])
        elif sig == '{ssha256}':
            matches.extend([6400])
        elif sig == '{ssha512}':
            matches.extend([6500])
        elif sig == '{ssha1}':
            matches.extend([6700])
        elif sig == '{x-issha, 1024}':
            matches.extend([10300])
        elif sig == '{PBKDF2_SHA256}':
            matches.extend([10901])
        elif sig == '{PKCS5S2}':
            matches.extend([12001])
        elif sig == '{CRAM-MD5}':
            matches.extend([16400])

        return matches

    def __find_hash_format_comma(self, hash):
        matches = []

        hash = hash.split(',')
        if hash[0] == 'v1;PPH1_MD4':
            matches.extend([12800])
        elif hash[0][:6] == 'pbkdf2':
            matches.extend([21600])

        return matches

    def __find_hash_format_dollar_within(self, hash):
        matches = []

        hash = hash.split('$')
        if hash[0] == 'sha1':
            matches.extend([124])
        elif hash[0] == 'pbkdf2_sha256':
            matches.extend([10000])
        elif self.__is_hex(hash[0], hash[1]):
            if len(hash[1]) <= 16:
                matches.extend([7700, 7701])
            else:
                matches.extend([7800, 7801])

        return matches

    def __find_hash_format_at(self, hash):
        matches = []

        hash = list(filter(len, hash.split('@')))
        if hash[0] == 'm':
            matches.extend([19000])
        elif hash[0] == 's':
            matches.extend([19100])
        elif hash[0] == 'S':
            matches.extend([19200])

        return matches

    def __find_hash_format_asterisk(self, hash):
        matches = []

        hash = hash.split('*')
        if hash[0] == 'WPA':
            matches.extend([22000, 22001])
        elif hash[0] == 'SQLCIPHER':
            matches.append(24600)

        return matches

    def __find_hash_format_misc(self, hash):
        matches = []

        if hash[:6] == '0x0100':
            matches.extend([131, 132])
        elif hash[:6] == '0x0200':
            matches.extend([1731])
        elif hash[:5] == '0xc00':
            matches.extend([8000])
        elif hash[:19] == 'grub.pbkdf2.sha512.':
            matches.extend([7200])
        elif hash[0] == '(' and hash[-1] == ')':
            matches.extend([8700, 9100])
        elif hash[0] == '_':
            matches.extend([12400])
        elif hash[:3] == 'eyJ':
            matches.extend([16500])
        elif self.__is_base64(True, hash):
            if len(hash) <= 16:
                matches.extend([1500, 2400, 16000, 24900])
            else:
                matches.extend([133, 501, 5700, 7000, 18800, 24800])

        return matches

    def __extract_braces(self, hash):
        index = hash.find('}') + 1
        return hash[:index], hash[index:]

    def __is_base64(self, include_dot, *args):
        chars = self.b64dot if include_dot else self.b64
        all_b64 = True
        for arg in args:
            if not all(c in chars for c in arg):
                all_b64 = False
                break
        return all_b64

    def __is_hex(self, *args):
        all_hex = True
        for arg in args:
            if not all(c in string.hexdigits for c in arg):
                all_hex = False
                break
        return all_hex

    def guess(self, hash):
        return [] if len(hash) == 0 else self.__find(hash)
