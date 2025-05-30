"""

Define the indicators in YARA style :-)

This file contains the rules used by the "emulate_payload.py" to 
identify the relevant part during the emulation.

"""

import yara

#
# Payload Name: [MSF] windows/meterpreter/reverse_tcp_rc4
# Search for  : mov esi,dword ptr [esi]
#               xor esi,0x<const>
# Used for    : this xor instruction contains the constant used to
#               encrypt the lenght of the payload that will be sent as 2nd
#               stage
# Architecture: x32
#
yara_reverse_tcp_rc4_xor_32 = 'rule reverse_tcp_rc4_xor {                \
                               strings:                                  \
                                   $opcodes_1 = { 8b 36                  \
                                                  81 f6 ?? ?? ?? ?? }    \
                               condition:                                \
                                   $opcodes_1 }'

rule_reverse_tcp_rc4_xor_32 = yara.compile(source=yara_reverse_tcp_rc4_xor_32)

#
# Payload Name: [MSF] windows/meterpreter/reverse_tcp_rc4
# Search for  : mov esi,esi
#               xor esi,0x<const>
# Used for    : this xor instruction contains the constant used to
#               encrypt the lenght of the payload that will be sent as 2nd
#               stage
# Architecture: x64
#
yara_reverse_tcp_rc4_xor_64 = 'rule reverse_tcp_rc4_xor {                \
                               strings:                                  \
                                   $opcodes_1 = { 89 f6                  \
                                                  81 f6 ?? ?? ?? ?? }    \
                               condition:                                \
                                   $opcodes_1 }'

rule_reverse_tcp_rc4_xor_64 = yara.compile(source=yara_reverse_tcp_rc4_xor_64)

#
# Payload Name: [MSF] windows/meterpreter/reverse_tcp_rc4
# Search for  : and dl, 0x0f
#               add bl, byte ptr [esi+edx]
# Used for    : the ptr is pointing to the RC4 key used to encrypt the
#               payload.
# Architecture: x32/x64
#
yara_reverse_tcp_rc4_key = 'rule reverse_tcp_rc4_key {                \
                            strings:                                  \
                                $opcodes_1 = { 80 e2 0f               \
                                               02 1C 16 }             \
                            condition:                                \
                                $opcodes_1 }'

rule_reverse_tcp_rc4_key = yara.compile(source=yara_reverse_tcp_rc4_key)

#
# Payload Name: [MSF] windows/encrypted_shell_reverse_tcp (chacha encrypted)
# Search for  : mov dword ptr ss:[esp+66],<const>
#               mov dword ptr ss:[esp+6A],<const>
# Used for    : this is the last instruction of the load of constants
#               with CHACHA key and nonce
#
# Architecture: x32
#
yara_encrypted_shell_reverse_tcp_32 = 'rule encrypted_shell_reverse_tcp {        \
                                    strings:                                     \
                                       $opcodes_1 = { C7 44 24 66                \
                                                      ?? ?? ?? ??                \
                                                      C7 44 24 6A                \
                                                      ?? ?? ?? ?? }              \
                                    condition:                                   \
                                        $opcodes_1 }'

rule_encrypted_shell_reverse_tcp_32 = yara.compile(
    source=yara_encrypted_shell_reverse_tcp_32)

#
# Payload Name: [MSF] windows/encrypted_shell_reverse_tcp (chacha encrypted)
# Search for  : mov byte ptr ss:[rsp+9F],0
#               call 176277E0870 (opcodes E835FEFFFF)
# Used for    : this is the last instruction of the load of constants
#               with CHACHA key and nonce
#
# Architecture: x64
#
yara_encrypted_shell_reverse_tcp_64 = 'rule encrypted_shell_reverse_tcp {        \
                                    strings:                                     \
                                       $opcodes_1 = { C6 84 24 ?? ?? ?? ?? ??    \
                                                      E8 35 FE FF FF  }          \
                                    condition:                                   \
                                        $opcodes_1 }'

rule_encrypted_shell_reverse_tcp_64 = yara.compile(
    source=yara_encrypted_shell_reverse_tcp_64)
