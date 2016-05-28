# IT Structure
# ============

import struct

IT_HEADER     = '<4x26s2x8H5BxHL4x128B'
IT_HEADER_INS = '<4x12sx3BH6BHBx26s6x120H'
IT_HEADER_SMP = '<4x12sx3B26s2B7L4B'
IT_HEADER_PAT = '<2H4x'

def parse_file(filename,
               with_instruments=False,
               with_samples=False,
               with_patterns=False):
    with open(filename, 'rb') as file:
        return parse(file,
                     with_instruments=with_instruments,
                     with_samples=with_samples,
                     with_patterns=with_patterns)

def parse(file,
          with_instruments=False,
          with_samples=False,
          with_patterns=False):

    data = struct.unpack(IT_HEADER, file.read(struct.calcsize(IT_HEADER)))

    info = {
        'songname':  data[0][:data[0].find('\0')],
        'ordnum':    data[1],
        'insnum':    data[2],
        'smpnum':    data[3],
        'patnum':    data[4],
        'version':   _get_version(data[5]),
        'compat':    _get_version(data[6]),
        'flags':     data[7],
        'special':   data[8],
        'globvol':   data[9],
        'mixvol':    data[10],
        'initspeed': data[11],
        'inittempo': data[12],
        'pansep':    data[13],
        'pantable':  data[16:80],
        'voltable':  data[80:144],
        'orders':    struct.unpack('<%dB' % data[1], file.read(data[1])),
    }
    
    insoffs = struct.unpack('<%dL' % data[2], file.read(data[2] * 4))
    smpoffs = struct.unpack('<%dL' % data[3], file.read(data[3] * 4))
    patoffs = struct.unpack('<%dL' % data[4], file.read(data[4] * 4))

    info['message'] = ''
    if data[8] & 0x01:
        file.seek(data[15])
        info['message'] = file.read(data[14] - 1).replace('\r', '\n')
        
    if with_instruments: info['instruments'] = _get_instruments(file, insoffs)
    if with_samples:     info['samples']     = _get_samples(file, smpoffs)
    if with_patterns:    info['patterns']    = _get_patterns(file, patoffs)
    
    return info

def _get_version(byte):
    ver = '%x' % byte
    return '%s.%s' % (ver[0], ver[1:])

def _get_instruments(file, offs):
    result = []

    for off in offs:
        file.seek(off)
        data = struct.unpack(IT_HEADER_INS, file.read(struct.calcsize(IT_HEADER_INS)))
        
        result.append({
            'filename': data[0][:data[0].find('\0')],
            'nna':      data[1],
            'dct':      data[2],
            'dca':      data[3],
            'fadeout':  data[4],
            'ppsep':    data[5],
            'ppcenter': data[6],
            'globvol':  data[7],
            'chanpan':  data[8],
            'rvolvar':  data[9],
            'rpanvar':  data[10],
            'trkvers':  data[11],
            'numsmp':   data[12],
            'name':     data[13].replace('\0', ' ').rstrip(),
            'smptable': map(lambda x: ((x & 0xff00) >> 8, x & 0x00ff), data[-120:]),
        })
        
    return result

def _get_samples(file, offs):
    result = []
    
    for off in offs:
        file.seek(off)
        data = struct.unpack(IT_HEADER_SMP, file.read(struct.calcsize(IT_HEADER_SMP)))
        
        result.append({
            'filename': data[0][:data[0].find('\0')],
            'globvol':  data[1],
            'flags':    data[2],
            'volume':   data[3],
            'name':     data[4].replace('\0', ' ').rstrip(),
            'convert':  data[5],
            'panning':  data[6],
            'length':   data[7],
            'loopbeg':  data[8],
            'loopend':  data[9],
            'c5spd':    data[10],
            'sustbeg':  data[11],
            'sustend':  data[12],
            'offset':   data[13],
            'vibspeed': data[14],
            'vibdepth': data[15],
            'vibrate':  data[16],
            'vibwave':  data[17],
        })
    
    return result

def _get_patterns(file, offs):
    result = []
    
    for off in offs:
        file.seek(off)
        data = struct.unpack(IT_HEADER_PAT, file.read(struct.calcsize(IT_HEADER_PAT)))
        result.append((_get_pattern_data(file, data[0], data[1]), data[1]))
        
    return result

def _get_pattern_data(file, length, numrows):
    result = []
       
    lastmask       = {}
    lastnote       = {}
    lastinstrument = {}
    lastvolpan     = {}
    lastcommand    = {}
    
    for i in range(numrows):
        row = []
        
        while length:
            field = {}
            
            channelvar = ord(file.read(1))
            length -= 1
            
            if channelvar == 0:
                # End of row.
                result.append(row)
                break
        
            field['channel'] = channel = (channelvar - 1) & 63
            
            if channelvar & 128:
                mask = lastmask[channel] = ord(file.read(1))
                length -= 1
            else:
                mask = lastmask.get(channel, 0)
            
            if mask & 1:
                field['note']    = lastnote[channel] = ord(file.read(1))
                field['notestr'] = note_to_string(field['note'])
                length -= 1
                
            if mask & 2:
                field['instrument'] = lastinstrument[channel] = ord(file.read(1))
                length -= 1
                
            if mask & 4:
                field['volpan'] = lastvolpan[channel] = ord(file.read(1))
                length -= 1
                
            if mask & 8:
                command = chr(ord('@') + ord(file.read(1)))
                value = ord(file.read(1))
                field['command'] = lastcommand[channel] = '%s%02X' % (command, value)
                length -= 2
                
            if mask & 16:
                field['note']    = lastnote[channel]
                field['notestr'] = note_to_string(field['note'])
                
            if mask & 32:
                field['instrument'] = lastinstrument[channel]
                
            if mask & 64:
                field['volpan'] = lastvolpan[channel]
                
            if mask & 128:
                field['command'] = lastcommand[channel]
                
            row.append(field)
            
    return result
    
NOTE_KEYS = ['C-', 'C#', 'D-', 'D#', 'E-', 'F-', 'F#', 'G-', 'G#', 'A-', 'A#', 'B-']
def note_to_string(note):
    if note == 254: return '^^^' # note cut
    if note == 255: return '===' # note off
    return '%s%d' % (NOTE_KEYS[note % 12], note / 12)
