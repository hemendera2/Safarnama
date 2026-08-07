# Private Alpha Release Checklist (v0.1.0-alpha.1)

## 📦 Versioning & Artifacts
- [x] Tag release version in Git (`git tag v0.1.0-alpha.1`).
- [x] Update `CHANGELOG.md` with features and known issues.
- [x] Freeze backend architecture (no new endpoints/models).

## 🛡️ Reliability & Operations
- [ ] **Rollback Procedure**: Documented and tested locally.
- [ ] **Backup Verification**: Verify `db/safarnama_v2.db` can be restored from a snapshot.
- [x] **Error Monitoring**: Structured JSON logging enabled for log aggregation.
- [ ] **Health Checks**: `/health` endpoint verified and monitored.

## ⚖️ Compliance & Trust
- [x] **Privacy Policy**: Drafted basic policy for user data and analytics tracking.
- [ ] **Cookie Consent**: UI banner implemented (if deploying in GDPR/relevant jurisdictions).
- [x] **Data Retention**: Set to 90 days for raw analytics events (internal policy).

## 🧪 Tester Support
- [ ] **Bug Reporting**: Dedicated channel/form created for alpha testers.
- [ ] **Issue Triage**: process defined for labeling and prioritizing alpha feedback.
- [ ] **Contact Channel**: `support@safarnama.in` verified.

## ✅ Product Readiness
- [x] **North Star Metrics**: Analytics dashboard (`/admin/insights`) verified.
- [x] **Seed Data**: Knowledge Graph populated with verified offbeat clusters.
- [x] **Performance**: API benchmarks passing (<10ms P95 for core discovery).
