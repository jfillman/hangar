// The Hangar tech stack: layers, tools, and why each one is there. Drawn on the homepage (FlightPath) and on /stack/.
// Verified against the repos on 2026-09-27: apron's bootstrap groups, airframe's XRDs and compositions, glidepath's
// catalog tasks and ADRs, and autopilot's README. Keep each status honest when the platform changes.
import type { Status } from './principles';

export type Layer = { key: string; name: string; product: string; why: string };
export type Tool = { layer: string; name: string; role: string; why: string; over?: string; status: Status; src: string };
export type Stage = { key: string; name: string; q: string; side: 'ci' | 'cluster'; why: string; tools: string[] };

export const layers: Layer[] = [
  {
    "key": "experience",
    "name": "Experience",
    "product": "tower",
    "why": "People should look in one place, and every change they make there should become a pull request."
  },
  {
    "key": "agents",
    "name": "AI workloads",
    "product": "autopilot",
    "why": "An agent is just another workload, with less authority by default and every call on the record."
  },
  {
    "key": "delivery",
    "name": "Delivery",
    "product": "glidepath",
    "why": "One small file for developers; a fixed, platform-owned path from a merged commit to a verified image."
  },
  {
    "key": "trust",
    "name": "Supply chain",
    "product": "glidepath",
    "why": "Signatures say who. Provenance says what the build actually did. A release gate needs both."
  },
  {
    "key": "release",
    "name": "Release",
    "product": "glidepath",
    "why": "ArgoCD is the only thing that writes to a cluster, and each cluster has its own."
  },
  {
    "key": "control",
    "name": "Control plane",
    "product": "airframe",
    "why": "The platform is an API. An XR says what you want; reconciliation keeps it true afterwards."
  },
  {
    "key": "ground",
    "name": "Ground",
    "product": "apron",
    "why": "Every cluster starts from the same template and the same bootstrap order, with its own trust roots."
  }
];

// Concerns that run through every layer rather than sitting in one.
export const rails: Layer[] = [
  {
    "key": "secrets",
    "name": "Secrets, identity and policy",
    "product": "hangar",
    "why": "No standing credentials where a cluster-issued identity will do, and no raw Secrets in git."
  },
  {
    "key": "observe",
    "name": "Observability",
    "product": "hangar",
    "why": "A release isn't done when it deploys. It's done when you can see whether it worked."
  }
];

export const tools: Tool[] = [
  {
    "layer": "experience",
    "name": "Backstage",
    "role": "The portal everything else plugs into.",
    "why": "I build on upstream Backstage and add plugins one at a time, so I know exactly what's in it and nothing needs a licence.",
    "over": "Red Hat Developer Hub",
    "status": "built",
    "src": "https://github.com/jfillman/hangar/blob/main/docs/backstage-design.md"
  },
  {
    "layer": "experience",
    "name": "Tower",
    "role": "Releases, promotions, canaries, SLOs and fleet views in one plugin.",
    "why": "A pane of glass that holds no cluster credentials. Every config change it offers becomes a GitOps pull request.",
    "status": "built",
    "src": "https://github.com/jfillman/tower"
  },
  {
    "layer": "experience",
    "name": "TechDocs",
    "role": "Docs next to the service they describe.",
    "why": "The same mkdocs files feed Backstage and this website, so there is only one copy to keep right.",
    "status": "built",
    "src": "https://github.com/jfillman/hangar/blob/main/web/README.md"
  },
  {
    "layer": "agents",
    "name": "Clearance",
    "role": "Policy, audit and session gateway for every agent tool call.",
    "why": "One choke point means one place to decide, spend budget and write the audit record. The core is built and tested; the real backends are still ahead.",
    "status": "built",
    "src": "https://github.com/jfillman/autopilot"
  },
  {
    "layer": "agents",
    "name": "MCP",
    "role": "The tool surface agents talk to.",
    "why": "A standard protocol, so any agent runtime can use Hangar without a custom client.",
    "status": "draft",
    "src": "https://github.com/jfillman/autopilot"
  },
  {
    "layer": "agents",
    "name": "CEL policy",
    "role": "Fifteen deny rules, each with an id and a fix hint.",
    "why": "Small, fast, side-effect free, and it fails closed. The same language Kyverno uses, so there's one policy idiom.",
    "status": "built",
    "src": "https://github.com/jfillman/autopilot"
  },
  {
    "layer": "agents",
    "name": "Preflight",
    "role": "Deterministic evaluations for every agent definition.",
    "why": "An agent definition is code, so it gets tests, including a check that each test can actually fail.",
    "status": "built",
    "src": "https://github.com/jfillman/autopilot"
  },
  {
    "layer": "agents",
    "name": "AgentRun XR",
    "role": "An ephemeral, scoped run as a namespaced Crossplane XR.",
    "why": "Durable changes stay commits; a run is short-lived, so it's an XR with a TTL, created directly, not a pull request.",
    "status": "draft",
    "src": "https://github.com/jfillman/autopilot"
  },
  {
    "layer": "agents",
    "name": "HolmesGPT",
    "role": "AI-assisted triage when a rollout goes wrong.",
    "why": "Dispatched from an Airframe function, so diagnosis rides the same control plane as everything else and only ever proposes a fix.",
    "status": "built",
    "src": "https://github.com/jfillman/airframe/tree/main/functions"
  },
  {
    "layer": "delivery",
    "name": "Tekton",
    "role": "The pipeline engine.",
    "why": "Runs on plain Kubernetes with no vendor lock-in, and developers never have to write its YAML.",
    "over": "Vendor-specific hosted CI",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0001-tekton-pipelines-as-code.md"
  },
  {
    "layer": "delivery",
    "name": "Pipelines-as-Code",
    "role": "Everything git-triggered: push, PR, tag, ChatOps.",
    "why": "Webhook signatures and PR status checks are easy to get wrong by hand. Its GitHub App does them properly.",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0001-tekton-pipelines-as-code.md"
  },
  {
    "layer": "delivery",
    "name": "CDEvents broker",
    "role": "Chains stages as events instead of one giant pipeline.",
    "why": "Each stage fails, retries and is observed on its own, and callers are authenticated with TokenReview rather than a key I'd have to guard.",
    "over": "One monolithic pipeline",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0002-cdevents-broker-tokenreview.md"
  },
  {
    "layer": "delivery",
    "name": "Kaniko",
    "role": "Builds images.",
    "why": "Rootless under Pod Security 'restricted', so the shared build identity never needs privilege on any cluster.",
    "over": "Docker-in-Docker, privileged buildah",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0010-kaniko-rootless-builds.md"
  },
  {
    "layer": "delivery",
    "name": "Semgrep",
    "role": "Static analysis in the pipeline.",
    "why": "Fast, rule-based and readable, and its result is attested, so a release can prove SAST actually ran.",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath"
  },
  {
    "layer": "delivery",
    "name": "Trivy",
    "role": "Image scanning and the CycloneDX SBOM.",
    "why": "One tool for both jobs, and both results land in the provenance a release gate checks.",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath"
  },
  {
    "layer": "delivery",
    "name": "Testkube",
    "role": "Runs each app's test workflows.",
    "why": "Tests as Kubernetes resources, fenced by a Kyverno policy so one tenant's tests can't read another's secrets.",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0007-testkube-shared-namespace.md"
  },
  {
    "layer": "trust",
    "name": "Tekton Chains",
    "role": "Signs images and writes SLSA provenance.",
    "why": "Provenance comes from the pipeline controller itself, not from a step a pipeline author could skip.",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0014-keyless-signing-two-trust-roots.md"
  },
  {
    "layer": "trust",
    "name": "Fulcio (self-hosted)",
    "role": "Keyless certificates for in-cluster build identities.",
    "why": "Public Fulcio only trusts a fixed list of CI issuers. My builds are Kubernetes service accounts, so they get their own root.",
    "over": "Long-lived signing keys",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0014-keyless-signing-two-trust-roots.md"
  },
  {
    "layer": "trust",
    "name": "Rekor",
    "role": "Transparency log for signatures.",
    "why": "A signature you can't look up later is a claim, not evidence.",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0014-keyless-signing-two-trust-roots.md"
  },
  {
    "layer": "trust",
    "name": "gitsign",
    "role": "Keyless commit signing for people.",
    "why": "Human identities are exactly what public Sigstore already trusts, so running my own for this would add cost for nothing.",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0014-keyless-signing-two-trust-roots.md"
  },
  {
    "layer": "trust",
    "name": "Conforma",
    "role": "Checks what the build actually did before release.",
    "why": "It validates the provenance's content (did SAST, scan and SBOM really run?), not just that a signature exists.",
    "over": "A bare cosign verify",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0015-provenance-policy-validates-attestation-input.md"
  },
  {
    "layer": "release",
    "name": "ArgoCD, one per cluster",
    "role": "The only writer to any cluster.",
    "why": "A hub ArgoCD holding every cluster's credentials is a path from dev into prod. Per-cluster instances keep the blast radius to one.",
    "over": "A central hub ArgoCD",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0005-multicluster-per-cluster-argocd.md"
  },
  {
    "layer": "release",
    "name": "ApplicationSets",
    "role": "Onboarding as a generator, not a ticket.",
    "why": "A new service appears because a commit landed in the right folder, never because someone ran a command.",
    "status": "built",
    "src": "https://github.com/jfillman/apron"
  },
  {
    "layer": "release",
    "name": "Helm",
    "role": "One application chart for every tier.",
    "why": "Secure defaults live in one versioned chart that every service and every cluster pins.",
    "over": "Kustomize remote bases",
    "status": "built",
    "src": "https://github.com/jfillman/hangar/blob/main/docs/gitops-strategy.md"
  },
  {
    "layer": "release",
    "name": "Argo Rollouts",
    "role": "Canaries with automated analysis.",
    "why": "A canary should feel like a conversation: pause, look, promote or roll back, all visible in Tower.",
    "status": "built",
    "src": "https://github.com/jfillman/apron"
  },
  {
    "layer": "control",
    "name": "Crossplane",
    "role": "The platform's API and reconciler.",
    "why": "People, portals, pipelines and agents all drive the same declarative API, and it keeps the result true afterwards.",
    "status": "built",
    "src": "https://github.com/jfillman/airframe"
  },
  {
    "layer": "control",
    "name": "Airframe XRDs",
    "role": "What a compliant service is: apps, data services, SLOs.",
    "why": "Node, Spring Boot, Go and Python apps, PostgreSQL, Redis, RabbitMQ and SLOs, each a small, schema-checked XR.",
    "status": "built",
    "src": "https://github.com/jfillman/airframe/tree/main/xrds"
  },
  {
    "layer": "control",
    "name": "Composition Functions",
    "role": "Turn an XR into real resources, and watch them.",
    "why": "go-templating for the plain cases; my own functions for the interesting ones, like watching a rollout.",
    "status": "built",
    "src": "https://github.com/jfillman/airframe/tree/main/functions"
  },
  {
    "layer": "control",
    "name": "provider-github",
    "role": "Repos, teams and branch protection as Crossplane resources.",
    "why": "A new service's repository is reconciled like anything else, so drift gets noticed and fixed.",
    "status": "built",
    "src": "https://github.com/jfillman/airframe"
  },
  {
    "layer": "control",
    "name": "CloudNativePG",
    "role": "PostgreSQL behind the database XR.",
    "why": "A real operator for failover and backups, hidden behind an XR small enough to ask for in one line.",
    "status": "built",
    "src": "https://github.com/jfillman/airframe/tree/main/xrds"
  },
  {
    "layer": "ground",
    "name": "Kubernetes",
    "role": "The execution substrate.",
    "why": "Plain upstream Kubernetes and nothing distribution-specific, so everything above it is portable.",
    "status": "built",
    "src": "https://github.com/jfillman/apron"
  },
  {
    "layer": "ground",
    "name": "Calico",
    "role": "Networking and network policy.",
    "why": "The template installs it before anything else, because a NetworkPolicy is only as real as the CNI enforcing it.",
    "status": "built",
    "src": "https://github.com/jfillman/apron"
  },
  {
    "layer": "ground",
    "name": "Contour + Gateway API",
    "role": "Ingress.",
    "why": "Gateway API is where ingress is going, and it separates the platform's listeners from each team's routes.",
    "status": "built",
    "src": "https://github.com/jfillman/apron"
  },
  {
    "layer": "ground",
    "name": "cert-manager",
    "role": "TLS everywhere, automatically.",
    "why": "Certificates nobody has to remember to renew.",
    "status": "built",
    "src": "https://github.com/jfillman/apron"
  },
  {
    "layer": "ground",
    "name": "Apron template",
    "role": "One cluster.yaml, one script, a known bootstrap order.",
    "why": "Copying the last cluster's repo and hoping nothing diverged is how the first two clusters drifted apart.",
    "over": "Hand-copied cluster repos",
    "status": "built",
    "src": "https://github.com/jfillman/apron"
  },
  {
    "layer": "secrets",
    "name": "Infisical",
    "role": "The secrets store.",
    "why": "Open source and self-hosted, with a proper API, so secrets are managed rather than hand-applied.",
    "over": "HashiCorp Vault, a cloud secrets manager",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0009-eso-infisical-secrets-backend.md"
  },
  {
    "layer": "secrets",
    "name": "External Secrets",
    "role": "Delivers secrets into every chart.",
    "why": "Every chart consumes an ExternalSecret; nobody ever applies a raw Secret by hand.",
    "over": "Hand-applied Secrets",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0009-eso-infisical-secrets-backend.md"
  },
  {
    "layer": "secrets",
    "name": "provider-infisical",
    "role": "Infisical projects and identities, declared.",
    "why": "The secrets system is configured through the same control plane as everything else, in git.",
    "status": "built",
    "src": "https://github.com/jfillman/provider-infisical"
  },
  {
    "layer": "secrets",
    "name": "TokenReview",
    "role": "Workload identity from the cluster itself.",
    "why": "A pod proves who it is with its own audience-bound token. No minting server, no key to leak.",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0002-cdevents-broker-tokenreview.md"
  },
  {
    "layer": "secrets",
    "name": "Kyverno",
    "role": "Admission policy where RBAC can't reach.",
    "why": "CEL-native ValidatingPolicy, used only where RBAC genuinely can't express the rule.",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0008-kyverno-testkube-secret-policy.md"
  },
  {
    "layer": "observe",
    "name": "OpenTelemetry",
    "role": "Traces every change from commit to release.",
    "why": "One trace per flow means a slow release has an answer, not a guess.",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath"
  },
  {
    "layer": "observe",
    "name": "Prometheus + Thanos",
    "role": "Metrics, kept long enough to matter.",
    "why": "The standard, with Thanos so DORA and SLO history survive past local retention.",
    "status": "built",
    "src": "https://github.com/jfillman/apron"
  },
  {
    "layer": "observe",
    "name": "Loki + Tempo",
    "role": "Logs and traces.",
    "why": "Same query model and same Grafana as the metrics, so one place to look.",
    "status": "built",
    "src": "https://github.com/jfillman/apron"
  },
  {
    "layer": "observe",
    "name": "Grafana",
    "role": "Dashboards, linked from Tower.",
    "why": "Deep dives live here; Tower links straight to the right panel.",
    "status": "built",
    "src": "https://github.com/jfillman/apron"
  },
  {
    "layer": "observe",
    "name": "Sloth",
    "role": "SLOs as code.",
    "why": "An SLO is an XR in git that generates its own recording and alerting rules.",
    "status": "built",
    "src": "https://github.com/jfillman/airframe/tree/main/xrds"
  },
  {
    "layer": "observe",
    "name": "DORA exporter",
    "role": "Delivery metrics from CDEvents.",
    "why": "Just another listener on the event stream, so the numbers come from what really happened.",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath"
  },
  {
    "layer": "observe",
    "name": "Tekton Results",
    "role": "Archived pipeline history.",
    "why": "Pruned PipelineRuns used to vanish after a day. Now you can look back at what a build really did.",
    "status": "built",
    "src": "https://github.com/jfillman/glidepath/blob/main/docs/admin/adr/0016-tekton-results-archival.md"
  }
];

// The route one change takes, for the flight-path view. Tools are referenced by name.
export const stages: Stage[] = [
  {
    "key": "declare",
    "name": "Declare",
    "q": "What do you want?",
    "side": "ci",
    "why": "Intent starts as a form in Tower or a file in git. Either way it ends as a commit.",
    "tools": [
      "Tower",
      "Backstage",
      "Airframe XRDs"
    ]
  },
  {
    "key": "compose",
    "name": "Compose",
    "q": "Make it real",
    "side": "ci",
    "why": "Crossplane turns a small XR into a repo, a pipeline, secrets and a database, then keeps them that way.",
    "tools": [
      "Crossplane",
      "Composition Functions",
      "provider-github",
      "provider-infisical",
      "CloudNativePG"
    ]
  },
  {
    "key": "build",
    "name": "Build",
    "q": "Does it build and pass?",
    "side": "ci",
    "why": "A fixed, platform-owned path. Stages are chained by events, so each one fails and retries on its own.",
    "tools": [
      "Pipelines-as-Code",
      "Tekton",
      "CDEvents broker",
      "Kaniko",
      "Semgrep",
      "Trivy",
      "Testkube"
    ]
  },
  {
    "key": "prove",
    "name": "Prove",
    "q": "Can we trust it?",
    "side": "ci",
    "why": "Who authorised it, and what the build actually did, are separate questions with separate answers.",
    "tools": [
      "gitsign",
      "Tekton Chains",
      "Fulcio (self-hosted)",
      "Rekor",
      "Conforma"
    ]
  },
  {
    "key": "release",
    "name": "Release",
    "q": "Ship it, safely",
    "side": "cluster",
    "why": "A release stage never touches a cluster. It opens a pull request, and each cluster's own ArgoCD pulls.",
    "tools": [
      "Helm",
      "ArgoCD, one per cluster",
      "ApplicationSets",
      "Argo Rollouts"
    ]
  },
  {
    "key": "watch",
    "name": "Watch",
    "q": "Did it work?",
    "side": "cluster",
    "why": "Outcomes come back as events, never as an API call reaching the other way.",
    "tools": [
      "OpenTelemetry",
      "Prometheus + Thanos",
      "Loki + Tempo",
      "Sloth",
      "DORA exporter",
      "Tower"
    ]
  }
];

export const toolByName = new Map(tools.map((t) => [t.name, t]));
