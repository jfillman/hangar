from libx import *

def w_fleets():
    b=[]
    b += [zone(24,100,320,340,'hangar cluster · type dev'), zone(384,224,256,120,'hub · type hub'), zone(680,100,296,340,'inference clusters · type inference')]
    b += [path([(184,240),(184,204)]), vlab(184,204,240,'MCP · LLM'),
          path([(184,304),(184,340)],dashed=True), vlab(184,304,340,'ATTACH'),
          path([(320,172),(704,172)],'link'), hlab(320,704,172,'OPENAI API · CALLER HEADER',LINK),
          path([(320,196),(352,196),(352,420),(408,420)],'link'),
          path([(616,272),(704,272)],'accent',dashed=True), hlab(616,704,272,'MANAGES',ACC),
          path([(828,204),(828,240)]), vlab(828,204,240,'ROUTES'),
          path([(828,304),(828,340)]), vlab(828,304,340,'WEIGHTS')]
    b += [node(48,140,272,64,'Clearance + model proxy','InfraService · dev only','focal'),
          node(48,240,272,64,'Agent runs','ephemeral · AgentRun claims'),
          node(48,340,272,64,'Shared backends','Postgres · Redis · queue · MinIO','store'),
          node(408,244,208,80,'Modelplane control plane','Crossplane · v1alpha1 · pinned'),
          node(408,388,208,64,'Hosted providers','API key stays in the proxy','external'),
          node(704,140,248,64,'InferenceGateway','OpenAI and Anthropic APIs'),
          node(704,240,248,64,'Serving stack + replicas','vLLM or any engine · GPU'),
          node(704,340,248,64,'Weight cache','ModelCache · shared storage','store')]
    b.append(callout(24,484,'The hub is the only holder of other clusters\' credentials, and only for GPU clusters with no app or agent data.'))
    b.append(legend(516,[('focal','Agent gate'),('store','State'),('external','Outside'),('link','Model API'),('accent-dash','Credential exception')]))
    return dict(slug='backend-fleets', eyebrow='Architecture · 09 of 19 · Backend fleets',
      title='Backend infrastructure: three fleet classes, one contract',
      desc='Architecture with three cluster classes: a Hangar dev cluster hosting Clearance with the model proxy, agent runs and shared backends; a hub running Modelplane on Crossplane; and dedicated inference clusters with an InferenceGateway, serving replicas and a weight cache; the model proxy reaches hosted providers or the inference gateway through one OpenAI-compatible contract, and the hub is the one place holding the credentials of other clusters.',
      lede='Hangar keeps managing agent workloads and their state. Self-hosted model serving is delegated to a separate fleet run by Modelplane, and the only thing Hangar depends on is an OpenAI or Anthropic compatible URL, so hosted providers and Modelplane are interchangeable behind the model proxy.',
      body=''.join(b), W=1000, H=564, y0=76,
      cards=[('Adopt, do not build','', P('Modelplane is Crossplane-native, written as Python composition functions with no controllers, and splits platform and ML personas the way Hangar does. It also provisions EKS and adopts any cluster (OKE today only by bring-your-own). Its API is v1alpha1 and v0.1, so it sits behind the contract and is pinned.')),
             ('Where it breaks your principles','accent', UL(['It holds cluster credentials, against no-cross-cluster-credentials. Contained: its own hub per environment, dedicated cloud accounts, clusters with no app or agent data.','It owns each inference cluster and installs Envoy Gateway, so it cannot share a Contour cluster.','Its Existing mode takes a kubeconfig Secret, a persisted credential. Unverified: whether short-lived cloud auth works there.'])),
             ('Managed the Hangar way','link', UL(['Hub config (InferenceClass, InferenceCluster, ModelDeployment) is durable and lives in git.','Replicas and scaling are runtime, derived by Modelplane and KEDA.','Cloud and provider keys come from Infisical through External Secrets, never git.','New apron cluster types: hub and inference.']))])

def w_egress():
    b=[]
    b += [zone(24,100,232,340,'sandbox · default-deny'), zone(312,100,272,340,'governed egress'), zone(640,100,336,340,'backends')]
    b += [path([(200,252),(284,252),(284,196),(336,196)],'link'), vlab(284,196,252,'MCP',LINK,'l'),
          path([(200,292),(284,292),(284,356),(336,356)],'link'), vlab(284,292,356,'LLM',LINK,'l'),
          path([(560,160),(664,160)]), hlab(560,664,160,'TIERED'),
          path([(560,232),(664,232)],dashed=True), hlab(560,664,232,'ALLOWLIST'),
          path([(560,320),(664,320)],'link'), hlab(560,664,320,'KEY IN PROXY',LINK),
          path([(560,392),(664,392)],'link'), hlab(560,664,392,'CALLER = RUN',LINK)]
    b += [node(48,236,152,72,'Agent run','any framework','input'),
          node(336,132,224,128,'Clearance','tools · policy · audit','focal'),
          node(336,292,224,128,'Model proxy','allowlist · budget · caller id','focal'),
          node(664,132,288,56,'Platform tools','repos · ArgoCD · Tekton · catalog'),
          node(664,204,288,56,'Third-party MCP','allowlisted hosts only','optional'),
          node(664,292,288,56,'Hosted models','Anthropic · OpenAI','external'),
          node(664,364,288,56,'Self-hosted models','Modelplane InferenceGateway','external')]
    b.append(callout(24,472,'Provider keys live only in the proxy. Nothing in the sandbox holds a credential.'))
    b.append(legend(504,[('focal','Egress gate'),('input','Agent run'),('backend','Backend'),('optional','Optional'),('link','Governed call')]))
    return dict(slug='model-and-tool-egress', eyebrow='Architecture · 10 of 19 · Model and tool plane',
      title='Two gates out of the sandbox: one for tools, one for models',
      desc='Architecture in which an agent run inside a default-deny sandbox has only two egress paths, to Clearance for tools and to the model proxy for models; Clearance reaches platform tools with tiers and allowlisted third-party MCP servers, while the model proxy holds provider keys and routes to hosted models or to a self-hosted Modelplane inference gateway using the session as the caller identity.',
      lede='Tools and models are governed separately because they fail differently. Tools change the world and are tiered and reversible in git. Models cost money and leak data, so they get an allowlist, a token budget and a caller identity that ties every request to a run.',
      body=''.join(b), W=1000, H=536, y0=76,
      cards=C3(P('Never-persisted credentials. Modelplane\'s gateway supports per-caller API keys, but a key per run is a persisted secret; its "behind another gateway" mode trusts an x-modelplane-caller header instead.'),
               UL(['The model proxy authenticates the run by TokenReview and sets x-modelplane-caller to the session id.','The inference gateway is reachable only from the proxy, so nothing else can set that header.','Modelplane stamps the caller on its usage records but advertises no usage caps or token metering, so budgets stay in the proxy.']),
               P('Unverified: what Modelplane\'s usage records contain (tokens, latency, model), and whether they can be joined to task_id. Read a real record before promising cost attribution.'), 'Unverified'))
