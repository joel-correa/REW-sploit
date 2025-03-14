

<img src="https://github.com/REW-sploit/Rs-files/blob/main/img/REW-sploit-Logo.png?raw=true|" width="300" alt="Logo" style="zoom:30%;" />

# REW-sploit

**The tool has been presented at Black-Hat Arsenal USA 2021**

https://www.blackhat.com/us-21/arsenal/schedule/index.html#rew-sploit-dissecting-metasploit-attacks-24086

Slides of presentation are available at https://github.com/REW-sploit/REW-sploit_docs

------

Need help in analyzing  Windows shellcode or attack coming from **Metasploit Framework** or **Cobalt Strike** (or may be also other malicious or obfuscated code)? Do you need to automate tasks with simple scripting? Do you want help to decrypt **MSF** generated traffic by extracting keys from payloads?

**REW-sploit** is here to help Blue Teams!

Here a quick demo:

[<img src="https://asciinema.org/a/ln8tkJH7bOhACFRMdnPmk2i1o.svg" alt="asciicast" width="700" style="zoom:33%;" />](https://asciinema.org/a/ln8tkJH7bOhACFRMdnPmk2i1o)

## Install

Installation is very easy. I strongly suggest to create  a specific Python Env for it:

```
# python -m venv <your-env-path>/rew-sploit
# source <your-env-path>/bin/activate
# git clone https://github.com/REW-sploit/REW-sploit.git
# cd REW-sploit
# pip install -r requirements.txt
# ./apply_patch.py -f
# ./rew-sploit
```

If you prefer, you can use the Dockerfile. To create the image:

```
docker build -t rew-sploit/rew-sploit .
```

and then start it (sharing the `/tmp/` folder):

```
docker run --rm -it --name rew-sploit -v /tmp:/tmp rew-sploit/rew-sploit
```

You see an `apply_patch.py` script in the installation sequence. This is required to apply a small patch to the `speakeasy-emulator` (https://github.com/fireeye/speakeasy/) to make it compatible with `REW-sploit`. You can easily revert the patch with `./apply_patch.py -r` if required.

Optionally, you can also install Cobalt-Strike Parser:

```
# cd REW-sploit/extras
# git clone https://github.com/Sentinel-One/CobaltStrikeParser.git
```



## Standing on the shoulder of giants

`REW-sploit` is based on a couple of great frameworks, `Unicorn` and `speakeasy-emulator` (but also other libraries). Thanks to everyone and thanks to the OSS movement!



## How it works

In general we can say that whilst Red Teams have a lot of tools helping them in "automating" attacks, Blue Teams are a bit "tool-less". So, what I thought is to build something to help Blue Team Analysis.

`REW-sploit` can get a shellcode/DLL/EXE, emulate the execution, and give you a set of information to help you in understanding what is going on. Example of extracted information are:

- API calls
- Encryption keys used by **MSF** payloads
- decrypted 2nd stage coming from **MSF**
- Cobalt-Strike configurations (if [CobaltStrike parser is installed](https://github.com/Sentinel-One/CobaltStrikeParser))

You can find several examples on the current capabilities here below:

- [RC4 Keys Extraction](https://asciinema.org/a/ln8tkJH7bOhACFRMdnPmk2i1o?speed=2)
- [RC4 Keys Extraction + PCAP 2nd stage decryption](https://asciinema.org/a/TfrcYnCaCuCPGVhaeq0wkEyag?speed=2)
- [ChaCha Keys Extraction](https://asciinema.org/a/01oMaPMG0BmLkPhXkIMNvSO4c?speed=2)
- [Meterpreter session Decryption (no RSA)](https://asciinema.org/a/Q8zZ8Ri7ZPzpBOZRTh9eZpzWi?speed=2)
- [Cobalt-Strike beacon Emulation](https://asciinema.org/a/ps4VdIqY71W786j9lOAz9taOp?speed=10)
- [Cobalt-Strike config Extraction](https://asciinema.org/a/1hGjmn9hgx5i2CAZFePpbaI70?speed=5)
- [Debugging options](https://asciinema.org/a/kIhOo2jKjOBTcxh8VrU0UzkXi)
- [Dumping Threads](https://asciinema.org/a/5SeKKodDXl79vceM7eXjsQJil?speed=2)



## Fixups

In some cases emulation was simply breaking, for different reasons. In some cases obfuscation was using some techniques that was confusing the emulation engine. So I implemented some ad-hoc fixups (you can enable them by using `-F` option of the `emulate_payload` command). Fixups are implemented in `modules/emulate_fixups.py`. Currently we have

Unicorn issue #1092:

```
    #
    # Fixup #1
    # Unicorn issue #1092 (XOR instruction executed twice)
    # https://github.com/unicorn-engine/unicorn/issues/1092
    #               #820 (Incorrect memory view after running self-modifying code)
    # https://github.com/unicorn-engine/unicorn/issues/820
    # Issue: self modfying code in the same Translated Block (16 bytes?)
    # Yes, I know...this is a huge kludge... :-/
    #
```

FPU emulation issue:

```
    #
    # Fixup #2
    # The "fpu" related instructions (FPU/FNSTENV), used to recover EIP, sometimes
    # returns the wrong addresses.
    # In this case, I need to track the first FPU instruction and then place
    # its address in STACK when FNSTENV is called
    #
```

Trap Flag evasion:

```
    #
    # Fixup #3
    # Trap Flag evasion technique
    # https://unit42.paloaltonetworks.com/single-bit-trap-flag-intel-cpu/
    #
    # The call of the RDTSC with the trap flag enabled, cause an unhandled
    # interrupt. Example code:
    #        pushf
    #        or dword [esp], 0x100
    #        popf
    #        rdtsc
    #
    # Any call to RDTSC with Trap Flag set will be intercepted and TF will
    # be cleared
    #
```



## Customize YARA rules

File `modules/emulate_rules.py` contains the **YARA** rules used to intercept the interesting part of the code, in order to implement instrumentation. I tried to comment as much as possible these sections in order to let you create your own rule (please share them with a pull request if you think they can help others). For example:

```
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
```



## Issues

Please, open Issues if you find something that not work or that can be improved. Thanks!
