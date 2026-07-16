# Heinrihs Skrodelis

```text
heinrihs@lab:~$ whoami
SCADA/ICS security researcher | IEC-104 | explainable IDS | CVD | AI-agent safety
```

I build defensive security artifacts for critical-infrastructure environments: IEC 60870-5-104 scenarios, SCADA/ICS detection rules, and benchmarks for checking whether AI assistants stay inside safe operational boundaries.

## Focus

- SCADA Agent Safety: simulation-only evaluation of LLM/agent behavior in control-room workflows
- IEC-104 Exposure Intelligence: synthetic scenarios, rules, and lab tooling for IEC 60870-5-104 security research
- Explainable IDS: operator-readable detection logic for industrial networks
- Coordinated vulnerability disclosure and protocol-aware OT product security
- Agent-assisted security workflows with human verification

## Featured Work

**SCADA / ICS**

- [SCADA Agent SafetyBench](https://github.com/heinrihs-s/Scada-Agent-SafetyBench) - simulation-only benchmark for AI assistants in SCADA/IEC-104 workflows
- [IEC-104 Threat Scenario Generator](https://github.com/heinrihs-s/IEC-60870-5-104-Threat-Scenario-Generator) - synthetic attack scenarios and lab artifacts for IDS evaluation
- [IEC-104 Rulebook](https://github.com/heinrihs-s/iec104-rulebook) - YAML monitoring rules and baseline templates
- [Zeek IEC-104 Lab](https://github.com/heinrihs-s/zeek-iec104-lab) - synthetic Zeek-style records and helper scripts

**Security Notes**

- [CTF Writeups](https://github.com/heinrihs-s/CTF-writeups/tree/main/SANS-European-Championship-2026) - SANS European Championship 2026 notes in messy hacker style
- [LogSpotAI](https://github.com/heinrihs-s/LogSpotAI) - tiny OpenAI-assisted log review experiment for defensive triage

## Public Vulnerability Research

- [CVE-2026-62972 - BACnet Stack](https://github.com/bacnet-stack/bacnet-stack/security/advisories/GHSA-9hq3-w3pc-8385) - discovered and responsibly reported an out-of-bounds read in the lighting command decoder; publicly credited as reporter
- [OpENer EtherNet/IP response-side buffer overflow](https://github.com/EIPStackGroup/OpENer/issues/576#issuecomment-4667180658) - co-discovered the remotely reachable defect in an independent report that was merged into issue #576; reproduced with AFL++/ASAN and developed regression-tested capacity guards for the serialization layer

## Working Style

Small reproducible artifacts. Synthetic data. No live-grid theatrics.

Python, Zeek-style logs, YAML rules, packet notes, CTF scars, Codex/Claude Code-friendly repos, and enough comments so a tired human can still review the decision.

## Elsewhere

- Site / CV: [heinrihs.org](https://heinrihs.org)
- Company route: securIT.lv
- Base: Riga, Latvia
