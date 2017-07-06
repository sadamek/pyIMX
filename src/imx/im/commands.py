# Copyright (c) 2017 Martin Olejar, martin.olejar@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from enum import Enum, unique
from struct import pack, unpack_from

from .header import CmdTag, Header


########################################################################################################################
## Custom Types
########################################################################################################################


class IntEnum(int, Enum):
    @classmethod
    def CheckValue(cls, value):
        for n, v in cls.__members__.items():
            if int(value) == int(v):
                return True
        return False

    @classmethod
    def StrToValue(cls, name):
        for n, v in cls.__members__.items():
            if name.upper() == n:
                return int(v)
        raise ValueError("Unsupported name: %s" % name)

    @classmethod
    def ValueToStr(cls, value):
        for n, v in cls.__members__.items():
            if int(value) == int(v):
                return n
        return "0x{0:08X}".format(value)

    @classmethod
    def GetNames(cls, lower=False):
        if lower:
            return [x.lower() for x in cls.__members__.keys()]
        else:
            return cls.__members__.keys()

    @classmethod
    def GetItems(cls):
        items = {}
        for n, v in cls.__members__.items():
            items[n] = int(v)
        return items


########################################################################################################################
## Enums
########################################################################################################################


@unique
class BytesEnum(IntEnum):
    ''' help '''
    BYTES_4 = 4
    BYTES_2 = 2
    BYTES_1 = 1


@unique
class WriteOpsEnum(IntEnum):
    ''' help '''
    WRITE_VALUE = 0
    WRITE_VALUE1 = 1
    CLEAR_BITMASK = 2
    SET_BITMASK = 3


@unique
class CheckOpsEnum(IntEnum):
    ''' help '''
    ALL_CLEAR = 0
    ALL_SET = 1
    ANY_CLEAR = 2
    ANY_SET = 3


@unique
class AlgorithmEnum(IntEnum):
    ''' Algorithm types '''
    HAB_ALG_ANY = 0x00
    HAB_ALG_HASH = 0x01
    HAB_ALG_SIG = 0x02
    HAB_ALG_F = 0x03
    HAB_ALG_EC = 0x04
    HAB_ALG_CIPHER = 0x05
    HAB_ALG_MODE = 0x06
    HAB_ALG_WRAP = 0x07
    HAB_ALG_SHA1 = 0x11
    HAB_ALG_SHA256 = 0x17
    HAB_ALG_SHA512 = 0x1b
    HAB_ALG_PKCS1 = 0x21
    HAB_ALG_AES = 0x55
    HAB_MODE_CCM = 0x66
    HAB_ALG_BLOB = 0x71


@unique
class ProtocolEnum(IntEnum):
    ''' Protocol tags '''
    HAB_PCL_SRK  = 0x03  # SRK certificate format
    HAB_PCL_X509 = 0x09  # X.509v3 certificate format
    HAB_PCL_CMS  = 0xC5  # CMS/PKCS#7 signature format
    HAB_PCL_BLOB = 0xBB  # SHW-specific wrapped key format
    HAB_PCL_AEAD = 0xA3  # Proprietary AEAD MAC format


@unique
class InsKeyEnum(IntEnum):
    ''' Command tags '''
    HAB_CMD_INS_KEY_CLR = 0
    HAB_CMD_INS_KEY_ABS = 1
    HAB_CMD_INS_KEY_CSF = 2
    HAB_CMD_INS_KEY_DAT = 4
    HAB_CMD_INS_KEY_CFG = 8
    HAB_CMD_INS_KEY_FID = 16
    HAB_CMD_INS_KEY_MID = 32
    HAB_CMD_INS_KEY_CID = 64
    HAB_CMD_INS_KEY_HSH = 128


@unique
class AuthEnum(IntEnum):
    ''' help '''
    HAB_CMD_AUT_DAT_CLR = 0
    HAB_CMD_AUT_DAT_ABS = 1


@unique
class EngineEnum(IntEnum):
    ''' Engine plugin tags '''
    HAB_ENG_ANY = 0x00
    HAB_ENG_SCC = 0x03
    HAB_ENG_RTIC = 0x05
    HAB_ENG_SAHARA = 0x06
    HAB_ENG_CSU = 0x0A
    HAB_ENG_SRTC = 0x0C
    HAB_ENG_DCP = 0x1B
    HAB_ENG_CAAM = 0x1D
    HAB_ENG_SNVS = 0x1E
    HAB_ENG_OCOTP = 0x21
    HAB_ENG_DTCP = 0x22
    HAB_ENG_ROM = 0x36
    HAB_ENG_HDCP = 0x24
    HAB_ENG_SW = 0xFF


@unique
class ItmEnum(IntEnum):
    ''' help '''
    HAB_VAR_CFG_ITM_MID = 0x01
    HAB_VAR_CFG_ITM_ENG = 0x03


########################################################################################################################
## HAB Commands
########################################################################################################################

class WriteDataCmd(object):
    ''' Write data command '''

    @property
    def bytes(self):
        return self._header.param & 0x7

    @bytes.setter
    def bytes(self, value):
        assert BytesEnum.CheckValue(value), "Unsupported Value !"
        self._header.param &= ~0x7
        self._header.param |= int(value)

    @property
    def ops(self):
        return (self._header.param >> 3) & 0x3

    @ops.setter
    def ops(self, value):
        assert WriteOpsEnum.CheckValue(value), "Unsupported Value !"
        self._header.param &= ~(0x3 << 3)
        self._header.param |= int(value) << 3

    @property
    def size(self):
        return self._header.length

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def __init__(self, bytes=BytesEnum.BYTES_4, ops=WriteOpsEnum.WRITE_VALUE):
        assert BytesEnum.CheckValue(bytes),  "Unsupported Value !"
        assert WriteOpsEnum.CheckValue(ops), "Unsupported Value !"
        self._header = Header(tag=CmdTag.HAB_CMD_WRT_DAT, param=((ops & 0x3) << 3) | (bytes & 0x7))
        self._wrdata = []

    def info(self):
        msg  = "-" * 60 + "\n"
        msg += "Write Data Command (Ops: {0:s}, Bytes: {1:d})\n".format(WriteOpsEnum.ValueToStr(self.ops), self.bytes)
        msg += "-" * 60 + "\n"
        for cmd in self._wrdata:
            msg += "- ADDR: 0x{0:08X}, VAL: 0x{1:08X}\n".format(cmd[0], cmd[1])
        return msg

    def append(self, address, value):
        assert 0 <= address <= 0xFFFFFFFF, "address out of range"
        assert 0 <= value <= 0xFFFFFFFF, "value out of range"
        self._wrdata.append([address, value])
        self._header.length += 8

    def pop(self, index):
        assert 0 <= index < len(self._wrdata)
        cmd = self._wrdata.pop(index)
        self._header.length -= 8
        return cmd

    def clear(self):
        self._wrdata.clear()
        self._header.length = self._header.size

    def parse(self, data, offset=0):
        self._header.parse(data, offset)
        tmp_size = self._header.size
        while tmp_size < self._header.length:
            assert (offset + tmp_size) < len(data)
            tmp = unpack_from(">LL", data, offset + tmp_size)
            self._wrdata.append(tmp)
            tmp_size += 8

    def export(self):
        raw_data = self._header.export()
        for cmd in self._wrdata:
            raw_data += pack(">LL", cmd[0], cmd[1])
        return raw_data


class CheckDataCmd(object):
    ''' Check data command '''

    @property
    def bytes(self):
        return self._header.param & 0x7

    @bytes.setter
    def bytes(self, value):
        assert BytesEnum.CheckValue(value), "uncorrected value !"
        self._header.param &= ~0x7
        self._header.param |= int(value)

    @property
    def ops(self):
        return (self._header.param >> 3) & 0x3

    @ops.setter
    def ops(self, value):
        assert CheckOpsEnum.CheckValue(value), "uncorrected value !"
        self._header.param &= ~(0x3 << 3)
        self._header.param |= int(value) << 3

    @property
    def size(self):
        return self._header.length

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def __init__(self, bytes=BytesEnum.BYTES_4, ops=CheckOpsEnum.ALL_SET):
        assert BytesEnum.CheckValue(bytes),  "uncorrected value !"
        assert CheckOpsEnum.CheckValue(ops), "uncorrected value !"
        self._header = Header(tag=CmdTag.HAB_CMD_CHK_DAT, param=((ops & 0x3) << 3) | (bytes & 0x7))
        self._chdata = []

    def info(self):
        msg  = "-" * 60 + "\n"
        msg += "Check Data Command (Ops: {0:s}, Bytes: {1:d})\n".format(WriteOpsEnum.ValueToStr(self.ops), self.bytes)
        msg += "-" * 60 + "\n"
        for cmd in self._chdata:
            msg += "- ADDR: 0x{0:08X}, VAL: 0x{1:08X}\n".format(cmd[0], cmd[1])
        return msg

    def append(self, address, value):
        assert 0 <= address <= 0xFFFFFFFF, "address out of range"
        assert 0 <= value <= 0xFFFFFFFF, "value out of range"
        self._chdata.append([address, value])
        self._header.length += 8

    def pop(self, index):
        assert 0 <= index < len(self._chdata)
        cmd = self._chdata.pop(index)
        self._header.length -= 8
        return cmd

    def clear(self):
        self._chdata.clear()
        self._header.length = self._header.size

    def parse(self, data, offset=0):
        self._header.parse(data, offset)
        tmp_size = self._header.size
        while tmp_size < self._header.length:
            assert (offset + tmp_size) < len(data)
            tmp = unpack_from(">LL", data, offset + tmp_size)
            self._chdata.append(tmp)
            tmp_size += 8

    def export(self):
        raw_data = self._header.export()
        for cmd in self._chdata:
            raw_data += pack(">LL", cmd[0], cmd[1])
        return raw_data


class NopCmd(object):
    ''' Nop command '''

    @property
    def size(self):
        return self._header.length

    def __init__(self, param=0):
        self._header = Header(tag=CmdTag.HAB_CMD_NOP, param=param)

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        msg = "-" * 60 + "\n"
        msg += "NOP Command\n"
        msg += "-" * 60 + "\n"
        return msg

    def parse(self, data, offset=0):
        self._header.parse(data, offset)

    def export(self):
        return self._header.export()


class SetCmd(object):
    ''' Set command '''

    @property
    def itm(self):
        return self._header.param

    @itm.setter
    def itm(self, value):
        assert ItmEnum.CheckValue(value), "uncorrected value !"
        self._header.param = int(value)

    @property
    def size(self):
        return self._header.length

    def __init__(self, itm = ItmEnum.HAB_VAR_CFG_ITM_ENG, data=None):
        assert ItmEnum.CheckValue(itm), "uncorrected value !"
        self._header = Header(tag=CmdTag.HAB_CMD_SET, param=itm)
        self._data = data if data else []

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        msg  = "-" * 60 + "\n"
        msg += "Set Command (ITM: {0:s})\n".format(ItmEnum.ValueToStr(self.itm))
        msg += "-" * 60 + "\n"
        for cmd in self._data:
            msg += "- ALG: {0:s}, ENG: {1:s}, CFG: {2:d}\n".format(AlgorithmEnum.ValueToStr(cmd[0]),
                                                                   EngineEnum.ValueToStr(cmd[1]), cmd[2])
        return msg

    def append(self, alg, eng, cfg):
        assert AlgorithmEnum.CheckValue(alg), "uncorrected value !"
        assert EngineEnum.CheckValue(eng), "uncorrected value !"
        assert type(cfg) is int, "cfg value must be INT type"
        assert 0 <= cfg < 256, "cfg value out of range"
        self._data.append([alg, eng, cfg])
        self._header.length += 4

    def pop(self, index):
        assert 0 <= index < len(self._data)
        cmd = self._data.pop(index)
        self._header.length -= 4
        return cmd

    def clear(self):
        self._data.clear()
        self._header.length = self._header.size

    def parse(self, data, offset=0):
        self._header.parse(data, offset)
        index = self._header.size
        while index < self._header.length:
            assert (offset + index) < len(data)
            (_, alg, eng, cfg) = unpack_from("4B", data, offset + index)
            self._data.append([alg, eng, cfg])
            index += 4

    def export(self):
        raw_data = self._header.export()
        for cmd in self._data:
            raw_data += pack("4B", 0x00, cmd[0], cmd[1], cmd[2])
        return raw_data


class InitializeCmd(object):
    ''' Initialize command '''

    @property
    def engine(self):
        return self._header.param

    @engine.setter
    def engine(self, value):
        assert EngineEnum.CheckValue(value), "uncorrected value !"
        self._header.param = int(value)

    @property
    def size(self):
        return self._header.length

    def __init__(self, engine=EngineEnum.HAB_ENG_ANY, data=None):
        assert EngineEnum.CheckValue(engine), "uncorrected value !"
        self._header = Header(tag=CmdTag.HAB_CMD_INIT, param=engine)
        self._data = data if data else []

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        msg  = "-" * 60 + "\n"
        msg += "Initialize Command (Engine: {0:s})\n".format(EngineEnum.ValueToStr(self.engine))
        msg += "-" * 60 + "\n"
        for val in self._data:
            msg += "- VAL: 0x{0:08X}\n".format(val)
        return msg

    def append(self, value):
        assert type(value) is int, "value must be INT type"
        assert 0 <= value < 0xFFFFFFFF, "value out of range"
        self._data.append(value)
        self._header.length += 4

    def pop(self, index):
        assert 0 <= index < len(self._data)
        val = self._data.pop(index)
        self._header.length -= 4
        return val

    def clear(self):
        self._data.clear()
        self._header.length = self._header.size

    def parse(self, data, offset=0):
        self._header.parse(data, offset)
        index = self._header.size
        while index < self._header.length:
            assert (offset + index) < len(data)
            val = unpack_from(">L", data, offset + index)
            self._data.append(val[0])
            index += 4

    def export(self):
        raw_data = self._header.export()
        for val in self._data:
            raw_data += pack(">L", val)
        return raw_data


class UnlockCmd(object):
    ''' Unlock engine command '''

    @property
    def engine(self):
        return self._header.param

    @engine.setter
    def engine(self, value):
        assert EngineEnum.CheckValue(value), "uncorrected value !"
        self._header.param = int(value)

    @property
    def size(self):
        return self._header.length

    def __init__(self, engine = EngineEnum.HAB_ENG_ANY, data=None):
        assert EngineEnum.CheckValue(engine), "uncorrected value !"
        self._header = Header(tag=CmdTag.HAB_CMD_UNLK, param=engine)
        self._data = data if data else []

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        msg  = "-" * 60 + "\n"
        msg += "Unlock Command (Engine: {0:s})\n".format(EngineEnum.ValueToStr(self.engine))
        msg += "-" * 60 + "\n"
        for val in self._data:
            msg += "- VAL: 0x{0:08X}\n".format(val)
        return msg

    def append(self, value):
        assert type(value) is int, "value must be INT type"
        assert 0 <= value < 0xFFFFFFFF, "value out of range"
        self._data.append(value)
        self._header.length += 4

    def pop(self, index):
        assert 0 <= index < len(self._data)
        val = self._data.pop(index)
        self._header.length -= 4
        return val

    def clear(self):
        self._data.clear()
        self._header.length = self._header.size

    def parse(self, data, offset=0):
        self._header.parse(data, offset)
        index = self._header.size
        while index < self._header.length:
            assert (offset + index) < len(data)
            val = unpack_from(">L", data, offset + index)
            self._data.append(val[0])
            index += 4

    def export(self):
        raw_data = self._header.export()
        for val in self._data:
            raw_data += pack(">L", val)
        return raw_data


class InstallKeyCmd(object):
    ''' Install key command '''
    @property
    def param(self):
        return self._header.param

    @param.setter
    def param(self, value):
        assert InsKeyEnum.CheckValue(value), "uncorrected value !"
        self._header.param = int(value)

    @property
    def pcl(self):
        return self._pcl

    @pcl.setter
    def pcl(self, value):
        assert ProtocolEnum.CheckValue(value), "uncorrected value !"
        self._pcl = int(value)

    @property
    def alg(self):
        return self._alg

    @alg.setter
    def alg(self, value):
        assert AlgorithmEnum.CheckValue(value), "uncorrected value !"
        self._alg = int(value)

    @property
    def src(self):
        return self._src

    @src.setter
    def src(self, value):
        self._src = value

    @property
    def tgt(self):
        return self._tgt

    @tgt.setter
    def tgt(self, value):
        self._tgt = value

    @property
    def keydat(self):
        return self._keydat

    @keydat.setter
    def keydat(self, value):
        self._keydat = value

    @property
    def size(self):
        return self._header.length

    def __init__(self, param=InsKeyEnum.HAB_CMD_INS_KEY_CLR,
                       pcl=ProtocolEnum.HAB_PCL_SRK,
                       alg=AlgorithmEnum.HAB_ALG_ANY,
                       src=0,
                       tgt=0,
                       keydat=0):
        self._header = Header(tag=CmdTag.HAB_CMD_INS_KEY, param=param)
        self.pcl = pcl
        self.alg = alg
        self.src = src
        self.tgt = tgt
        self.keydat = keydat
        self._hash = []

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        msg = "-" * 60 + "\n"
        msg += "Install Key Command\n"
        msg += " Flag:   {0:s}\n".format(InsKeyEnum.ValueToStr(self.param))
        msg += " Prot:   {0:s}\n".format(ProtocolEnum.ValueToStr(self.pcl))
        msg += " Algo:   {0:s}\n".format(AlgorithmEnum.ValueToStr(self.alg))
        msg += " SrcKey: {0:d} (Source key index) \n".format(self.src)
        msg += " TgtKey: {0:d} (Target key index) \n".format(self.tgt)
        msg += " Addr:   0x{0:08X} (Start address of key data to install) \n".format(self.keydat)
        msg += "-" * 60 + "\n"
        return msg

    def parse(self, data, offset=0):
        self._header.parse(data, offset)
        (self.pcl, self.alg, self.src, self.tgt, self.keydat) = unpack_from(">BBBBL", data, offset + self._header.size)
        index = self._header.size + 8
        while index < self._header.length:
            assert (offset + index) < len(data)
            val = unpack_from(">L", data, offset + index)
            self._hash.append(val)
            index += 4


    def export(self):
        raw_data = self._header.export()
        raw_data += pack(">BBBBL", self.pcl, self.alg, self.src, self.tgt, self.keydat)
        for val in self._hash:
            raw_data += pack(">L", val)
        return raw_data


class AuthDataCmd(object):
    ''' write here Doc '''
    @property
    def flag(self):
        return self._header.param

    @flag.setter
    def flag(self, value):
        assert AuthEnum.CheckValue(value), "uncorrected value !"
        self._header.param = int(value)

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    @property
    def pcl(self):
        return self._pcl

    @pcl.setter
    def pcl(self, value):
        assert ProtocolEnum.CheckValue(value), "uncorrected value !"
        self._pcl = int(value)

    @property
    def eng(self):
        return self._eng

    @eng.setter
    def eng(self, value):
        assert EngineEnum.CheckValue(value), "uncorrected value !"
        self._eng = int(value)

    @property
    def cfg(self):
        return self._cfg

    @cfg.setter
    def cfg(self, value):
        self._cfg = value

    @property
    def auth_start(self):
        return self._auth_start

    @auth_start.setter
    def auth_start(self, value):
        self._auth_start = value

    @property
    def auth_data(self):
        return self._auth_data

    @auth_data.setter
    def auth_data(self, value):
        self._auth_data = value

    @property
    def size(self):
        return self._header.length

    def __init__(self, flag=AuthEnum.HAB_CMD_AUT_DAT_CLR,
                       key=0,
                       pcl=ProtocolEnum.HAB_PCL_SRK,
                       eng=EngineEnum.HAB_ENG_ANY,
                       cfg=0,
                       auth_start=0,
                       auth_data=None):
        self._header = Header(CmdTag.HAB_CMD_AUT_DAT, flag)
        self.key = key
        self.pcl = pcl
        self.eng = eng
        self.cfg = cfg
        self.auth_start = auth_start
        self.auth_data = auth_data
        self._blocks = []

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        msg = "-" * 60 + "\n"
        msg += "Auth Data Command\n"
        msg += " Flag:   {0:s}\n".format(AuthEnum.ValueToStr(self._header.param))
        msg += " Prot:   {0:s}\n".format(ProtocolEnum.ValueToStr(self.pcl))
        msg += " Engine: {0:s}\n".format(EngineEnum.ValueToStr(self.eng))
        msg += " Key:    {0:d} (Key address)\n".format(self.key)
        msg += " Conf:   {0:d} (Configuration)\n".format(self.cfg)
        msg += " Addr:   0x{0:08X} (Start address of authentication data) \n".format(self.auth_start)
        msg += "-" * 60 + "\n"
        for blk in self._blocks:
            msg += "- Start: 0x{0:08X}, Length: {1:d} Bytes\n".format(blk[0], blk[1])
        return msg

    def append(self, start_address, size):
        self._blocks.append([start_address, size])
        self._header.length += 8

    def pop(self, index):
        assert 0 <= index < len(self._blocks)
        block = self._blocks.pop(index)
        self._header.length -= 8
        return block

    def clear(self):
        self._blocks.clear()
        self._header.length = self._header.size

    def parse(self, data, offset=0):
        self._header.parse(data, offset)
        index = self._header.size
        (key, pcl, eng, cfg, auth_start) = unpack_from(">BBBBL", data, offset + index)
        self.key = key
        self.pcl = pcl
        self.eng = eng
        self.cfg = cfg
        self.auth_start = auth_start
        index += 8
        while index < self._header.length:
            blk = unpack_from(">2L", data, offset + index)
            self._blocks.append(blk)
            index += 8

    def export(self):
        raw_data  = self._header.export()
        raw_data += pack(">BBBBL", self.key, self.pcl, self.eng, self.cfg, self.auth_start)
        for blk in self._blocks:
            raw_data += pack(">2L", blk[0], blk[1])
        return raw_data