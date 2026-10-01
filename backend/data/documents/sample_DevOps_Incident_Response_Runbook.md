# Enterprise DevOps Incident Response Runbook
Document Ref: SRE-RUNBOOK-2026-V3
Owner: Site Reliability Engineering & Platform Security Team
Last Review: 2026-08-15

## 1. Severity Levels & SLA Targets
Incidents are categorized into four severity classifications based on user impact and financial risk:

| Severity | Definition | Initial Response SLA | Status Update Cadence | Post-Mortem Required? |
| :--- | :--- | :--- | :--- | :--- |
| **SEV-1 (Critical)** | Core service outage affecting >10% of global customers or critical data loss. | Within 15 minutes | Every 15 minutes | Yes, within 48 hours |
| **SEV-2 (Major)** | Major functionality impaired with no viable workaround; high latency (>2s). | Within 30 minutes | Every 30 minutes | Yes, within 72 hours |
| **SEV-3 (Moderate)** | Non-critical component degraded; workaround exists. | Within 2 hours | Every 2 hours | Optional |
| **SEV-4 (Minor)** | Minor bug or cosmetic defect with minimal customer disruption. | Within 24 hours | On resolution | No |

## 2. Incident Command System (ICS) Roles
When a SEV-1 or SEV-2 is triggered, the following roles are assigned immediately:
1. **Incident Commander (IC)**: Holds single-threaded authority on all tactical decisions. Does not write code or touch infrastructure; directs the team.
2. **Operations Lead**: Manages hands-on troubleshooting, runs rollbacks, or applies configuration toggles.
3. **Communications Lead**: Updates executive leadership, customer support, and the public status page (`status.enterprise.corp`).
4. **Scribe**: Logs every timestamped action, hypothesis, and command executed in the incident war room.

## 3. Communication Protocols
- Dedicated Slack Channel: `#incident-war-room-[incident-number]`
- Zoom Bridge: Link automatically generated in the Slack header via PagerDuty bot.
- Status Page Updates: Must be published within 20 minutes of SEV-1 declaration using standardized pre-approved templates.

## 4. Disaster Recovery (DR) Metrics
- **RPO (Recovery Point Objective)**: Maximum allowable data loss window is 15 minutes. Backups are snapshotted across multi-region object storage every 10 minutes.
- **RTO (Recovery Time Objective)**: Maximum downtime allowable to restore critical operations is 60 minutes for tier-1 services.
- Multi-Region Failover: Automated DNS route switching via Route53 health checks initiates failover to the secondary region if primary region health probes fail for 3 consecutive checks.
