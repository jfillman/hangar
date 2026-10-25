"""Spec: Airframe cloud dependencies - MessageQueue, ObjectStorage, ManagedPostgreSQL (Oct 24, 2026)."""
from report import Page, chip, esc
import lib
from lib import node, path, zone, hlab, vlab, text

P = Page(
    'airframe-cloud-dependencies', 'Spec', 'Airframe · Spec · Cloud dependencies',
    'Managed cloud services an app can depend on, on AWS or Azure',
    'Three new Airframe kinds give a Hangar app a queue, object storage or a PostgreSQL database run by the cloud '
    'provider: what each creates on AWS and Azure, the guardrails with no field to turn them off, how a Lambda function '
    'gets access without a key, and what the live run on October 24, 2026 showed.',
    '2026-10-24',
    meta=[('Status', 'AWS verified live, Oct 24, 2026; Azure render-tested, never run'),
          ('Version', 'Airframe v0.3.165 · airframe#123, #124, #125'),
          ('Docs', '<a href="https://hangarplatform.dev/docs/airframe/user/cloud-dependencies/">Cloud dependencies</a> · '
                   '<a href="https://hangarplatform.dev/docs/airframe/admin/cloud-credentials/">Airframe cloud credentials</a>')],
    lede=('Until now an app on a cloud target could run in the cloud, but whatever it depended on had to come from '
          'somewhere else. Three new kinds in <code>catalog.hangar.io/v1alpha1</code> close that: a queue, object '
          'storage and a PostgreSQL database, each run by the cloud provider. You ask for one the way you ask for a cloud '
          'target, with a manifest in the app\'s <code>xr-requests/</code>, and you delete it the same way. One field '
          'picks the cloud. Everything else means the same thing on both.'))

P.add("""
<div class="verdict ok">
  <span class="stamp">AWS verified live · Oct 24, 2026</span>
  <h2>A queue, a bucket and a database, asked for in git, with the guardrails already on.</h2>
  <ul>
    <li><b>One request, the right pieces.</b> <code>spec.cloud</code> is <code>aws</code> by default or <code>azure</code>, fixed at creation. The composition creates every supporting piece and deletes all of them with the XR.</li>
    <li><b>Private and encrypted, with no field to change that.</b> No bucket can be made public, nothing is stored unencrypted, and the database refuses plaintext connections.</li>
    <li><b>Grants, not keys.</b> On AWS a Lambda function gets a policy on its own role for this one queue or bucket, capped by the permissions boundary.</li>
    <li><b>Status a script can branch on.</b> One condition, <code>DependencyReady</code>, with a fixed set of reasons.</li>
  </ul>
</div>
""")

# Figure 1: grants and triggers, not keys.
W, H = 760, 372
b = zone(24, 24, 224, 300, 'Dev cluster · app-baggage-api-cicd')
b += zone(264, 24, 472, 300, 'AWS account · one region')
b += (f'<rect x="528" y="220" width="200" height="96" rx="8" fill="rgba(185,121,31,0.05)" '
      f'stroke="rgba(185,121,31,0.50)" stroke-width="1" stroke-dasharray="4,4"/>')
b += text(628, 308, 'PERMISSIONS BOUNDARY', 8, 500, lib.ACC, anchor='middle', mono=True, ls='0.14em')
b += path([(228, 92), (280, 92)]) + hlab(228, 280, 92, 'creates')
b += path([(464, 92), (536, 92)], 'link') + hlab(464, 536, 92, 'triggers', lib.LINK)
b += path([(374, 120), (374, 228)], 'accent') + vlab(374, 120, 228, 'after N tries', lib.ACC)
b += path([(628, 232), (628, 124)]) + vlab(628, 124, 232, 'runs as')
b += path([(134, 120), (134, 228)], dashed=True) + vlab(134, 120, 228, 'looks up')
b += path([(134, 288), (134, 344), (628, 344), (628, 280)], 'accent') + hlab(134, 628, 344, 'a grant on its role, not a key', lib.ACC)
b += node(40, 64, 188, 56, 'MessageQueue', 'baggage-scans · the XR', 'focal')
b += node(40, 232, 188, 56, 'AwsLambdaTarget', 'baggage-api', 'backend')
b += node(284, 64, 180, 56, 'SQS queue', 'encrypted · redrive', 'backend')
b += node(284, 232, 180, 56, 'Dead-letter queue', 'baggage-scans-dlq', 'store')
b += node(540, 64, 180, 56, 'Lambda function', 'invoked with batches', 'external')
b += node(540, 232, 176, 48, 'baggage-api-exec', 'inline policy · this queue', 'backend')
fig1 = P.fig(b, W, H, 'Grants and triggers, not keys',
             'On the dev cluster, a MessageQueue XR named baggage-scans lists the AwsLambdaTarget baggage-api as a consumer. The composition looks the target up, creates an encrypted SQS queue with a dead-letter queue in AWS, connects the queue to the Lambda function with an event source mapping, and writes an inline policy for this queue only onto the function\'s execution role, inside the permissions boundary. Messages that fail N times move to the dead-letter queue.',
             'ObjectStorage works the same way, without the trigger. Removing a consumer removes its grant and its trigger. A consumer that names a target that doesn\'t exist, or one in another region, gets nothing, and the status says which.')

# Figure 2: the life of a dependency.
W2, H2 = 760, 196
steps = [('Commit the XR', 'xr-requests/ in git', 'input'), ('Composition', 'creates every piece', 'focal'),
         ('DependencyReady', 'a fixed set of reasons', 'backend'), ('App reads it', 'a ConfigMap, a Secret', 'store'),
         ('Delete the file', 'removes all of it', 'backend')]
c = ''
for i, (n, s, k) in enumerate(steps):
    x = 24 + i * 144
    c += node(x, 40, 136, 56, n, s, k)
    if i:
        c += path([(x - 8, 68), (x - 1, 68)], 'accent' if i == 1 else 'muted', marker=False)
c += text(24, 136, 'A queue or a bucket is ready in under a minute. A new database takes 5 to 15 minutes.', 11, fill=lib.MUTED)
c += text(24, 156, 'A bucket with objects in it is kept unless emptyOnDelete says otherwise; protect adds RDS deletion protection.', 11, fill=lib.MUTED)
fig2 = P.fig(c, W2, H2, 'The life of a cloud dependency',
             'Five steps: commit the XR into the app\'s xr-requests folder; the composition creates every piece; DependencyReady reports with a fixed set of reasons; the app reads a ConfigMap and, where there is one, a Secret, both named after the XR; deleting the file removes all of it.',
             'The same lifecycle as every other Airframe request, so a person, a Backstage form or an agent asks for a database exactly the way it asks for a function.')

cells = lambda items: '<ul class="plain">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
kinds = [
    ('MessageQueue', 'A durable queue with a dead-letter queue. On AWS it can trigger a Lambda function.',
     ['SQS queue, server-side encryption with SQS-owned keys', 'Dead-letter queue <code>&lt;name&gt;-dlq</code>, kept 14 days',
      'Per consumer: an IAM grant, and an event source mapping if it\'s a trigger'],
     ['Resource group, owned by the XR', 'Service Bus namespace (Basic) and queue', 'A listen and send policy for this queue only'],
     '<code>queueName</code>, <code>fifo</code>, <code>lockSeconds</code>, <code>retentionSeconds</code>, <code>deadLetter</code>, <code>consumers[]</code>'),
    ('ObjectStorage', 'A private, encrypted bucket for files and blobs, with access for Lambda functions.',
     ['S3 bucket', 'Block Public Access, ownership enforced, SSE-S3', 'Optional versioning', 'Per consumer: an IAM grant'],
     ['Resource group, owned by the XR', 'StorageV2 account, TLS 1.2, HTTPS only', 'One private blob container'],
     '<code>bucketName</code>, <code>versioning</code>, <code>emptyOnDelete</code>, <code>consumers[]</code>'),
    ('ManagedPostgreSQL', 'One PostgreSQL database, TLS only, reachable only from the networks you list.',
     ['Its own VPC, two subnets in two zones', 'Security group, one rule per allowed CIDR', 'RDS for PostgreSQL 16 or 17, encrypted'],
     ['Resource group, owned by the XR', 'Flexible Server and its database', 'One firewall rule per allowed CIDR'],
     '<code>size</code>, <code>version</code>, <code>storageGiB</code>, <code>databaseName</code>, <code>allowedCidrs</code>, <code>protect</code>'),
]
krows = ''.join(f'<tr><td class="area">{k}</td><td>{cells(a)}</td><td>{cells(z)}</td></tr>' for k, w, a, z, f in kinds)
kfields = ''.join(f'<li><b>{k}</b>: {f}</li>' for k, w, a, z, f in kinds)

PRE = 'margin:0;padding:14px 16px;font-family:var(--mono);font-size:.8rem;line-height:1.5'
reasons = [
    ('ok', '…Ready', 'Every piece is ready. The connection details are in the ConfigMap.'),
    ('info', '…Provisioning', 'Something is still being created. The message names what is pending.'),
    ('warn', '…ConsumerUnresolved', 'Queue or storage only. It\'s ready, but a <code>consumers[]</code> entry names no target here, or one in another region.'),
    ('warn', 'MessageQueueNeedsAwsAccount', 'The cluster registry names no AWS account, so the queue\'s ARN is unknown and nothing is created.'),
    ('bad', 'ManagedPostgreSQLFailing', 'The provider can\'t create the server: a taken name, a quota, an unavailable instance class. The message carries its error.'),
]
STATE = {'ok': 'Ready', 'info': 'Working', 'warn': 'Attention', 'bad': 'Failing'}
rrows = ''.join(f'<tr><td class="area"><code>{r}</code></td><td>{chip(STATE[tone], tone)}</td><td>{m}</td></tr>' for tone, r, m in reasons)
checks = [
    ('Ready', 'Queue, bucket and Lambda target ready in about 4 minutes, the database in about 7. <code>airframe-verify</code> passed every step for each kind.'),
    ('Grants', 'The IAM policy simulator, boundary included, allowed this queue and this bucket, and denied any other.'),
    ('Trigger', 'One message invoked the function twice, matching <code>maxReceiveCount: 2</code>. Both runs failed on purpose, because the placeholder image has no handler, and the message moved to the dead-letter queue.'),
    ('Bucket', 'All four public-access blocks on, ownership enforced. An object written and read back was encrypted with AES256.'),
    ('Database', 'PostgreSQL 17.9 on db.t4g.micro, encrypted, admitting one /32. <code>psql</code> connected over TLS 1.3. A connection with <code>sslmode=disable</code> was refused.'),
    ('Teardown', 'Removing the file deleted the queues, the bucket and its object, the instance, the VPC, the function, the repository, the roles and the password Secret. No snapshot was left.'),
]
crows = ''.join(f'<tr><td class="area">{k}</td><td>{chip("Pass", "ok")}</td><td>{v}</td></tr>' for k, v in checks)

P.add(f"""
<section>
  <h2>Three kinds</h2>
  <div class="cards">
    <div class="card"><span class="eyebrow">Amazon SQS · Service Bus</span><h3>MessageQueue</h3><p>A durable queue with a dead-letter queue. On AWS it can trigger a Lambda function.</p></div>
    <div class="card"><span class="eyebrow">Amazon S3 · Storage Account</span><h3>ObjectStorage</h3><p>A private, encrypted bucket for files and blobs, with access for Lambda functions.</p></div>
    <div class="card"><span class="eyebrow">Amazon RDS · Flexible Server</span><h3>ManagedPostgreSQL</h3><p>One PostgreSQL database, TLS only, reachable only from the networks you list.</p></div>
  </div>
</section>

<section>
  <h2>One request, the right pieces on each cloud</h2>
  <div class="prose"><p><code>spec.cloud</code> is <code>aws</code> by default and can't change after creation. The composition creates every supporting piece, and deletes all of them with the XR.</p></div>
  <div class="tbl"><table>
    <thead><tr><th>Kind</th><th>On AWS</th><th>On Azure</th></tr></thead>
    <tbody>{krows}</tbody>
  </table></div>
  <p class="note">Key fields:</p>
  <ul class="plain">{kfields}</ul>
</section>

<section>
  <h2>Guardrails you get without asking</h2>
  <div class="prose"><p>None of these has a field to turn it off. That's deliberate: the absence of the field is the policy.</p></div>
  <div class="cards">
    <div class="card"><span class="eyebrow">All kinds</span><h3>Private by default</h3><p>No field makes a bucket public. All four S3 public-access blocks are on and ACLs are disabled. An Azure account allows no public blobs. A database admits no network until <code>allowedCidrs</code> lists one.</p></div>
    <div class="card"><span class="eyebrow">All kinds</span><h3>Encrypted, TLS only</h3><p>Queues, buckets and database storage are encrypted at rest. PostgreSQL refuses plaintext connections on both clouds. Storage accepts only HTTPS with TLS 1.2 or later.</p></div>
    <div class="card"><span class="eyebrow">Consumers</span><h3>No access keys on AWS</h3><p>A Lambda consumer gets an inline policy on its own execution role for this one queue or bucket. The <code>HangarCloudTargetBoundary</code> permissions boundary caps every grant.</p></div>
    <div class="card"><span class="eyebrow">Deletion</span><h3>No accidental data loss</h3><p>A bucket that holds objects is kept unless <code>emptyOnDelete</code> is set. Azure always deletes contents, so it has to say so. <code>protect</code> adds RDS deletion protection and a final snapshot.</p></div>
  </div>
</section>

<section>
  <h2>How a Lambda function gets access</h2>
  <div class="prose"><p>List an <code>AwsLambdaTarget</code> in <code>consumers[]</code>. The composition looks it up in the same namespace and writes a scoped policy onto that function's execution role. With <code>trigger: true</code> it also connects the queue to the function.</p></div>
  {fig1}
  <div class="tbl"><table>
    <thead><tr><th>Kind</th><th>access</th><th>Actions, on this queue or bucket only</th></tr></thead>
    <tbody>
      <tr><td class="area">MessageQueue</td><td><code>send</code></td><td><code>SendMessage</code></td></tr>
      <tr><td class="area"></td><td><code>receive</code></td><td><code>ReceiveMessage</code>, <code>DeleteMessage</code>, <code>ChangeMessageVisibility</code></td></tr>
      <tr><td class="area"></td><td><code>sendReceive</code></td><td>Both of the above (the default). Every queue grant also includes <code>GetQueueAttributes</code> and <code>GetQueueUrl</code>.</td></tr>
      <tr><td class="area">ObjectStorage</td><td><code>read</code></td><td><code>ListBucket</code>, <code>GetBucketLocation</code>, <code>GetObject</code></td></tr>
      <tr><td class="area"></td><td><code>readWrite</code></td><td>Also <code>PutObject</code>, <code>DeleteObject</code> and multipart uploads (the default)</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <h2>Request one</h2>
  <div class="prose"><p>Put the manifest in <code>tenants/&lt;app&gt;/xr-requests/</code> of the dev cluster's tenants repo. It lands in <code>app-&lt;app&gt;-cicd</code> on the dev cluster, where the cloud providers run. These are not <code>components:</code> entries. Here is Skyport's baggage-api asking for all three.</p></div>
  <div class="tbl"><pre style="{PRE}">apiVersion: catalog.hangar.io/v1alpha1
kind: MessageQueue
metadata:
  name: baggage-scans
spec:
  lockSeconds: 60              # at least the function's timeout, for a trigger
  deadLetter:
    maxReceiveCount: 5         # then the message moves to baggage-scans-dlq
  consumers:
    - awsLambdaTarget: baggage-api   # an AwsLambdaTarget in the same namespace
      access: receive
      trigger: true                  # the queue invokes the function
      batchSize: 10
---
apiVersion: catalog.hangar.io/v1alpha1
kind: ObjectStorage
metadata:
  name: baggage-exports
spec:
  bucketName: skyport-baggage-exports   # S3 names are global across AWS
  versioning: true
  consumers:
    - awsLambdaTarget: baggage-api
      access: readWrite
---
apiVersion: catalog.hangar.io/v1alpha1
kind: ManagedPostgreSQL
metadata:
  name: baggage-db
spec:
  size: small                 # db.t4g.micro on AWS, B_Standard_B1ms on Azure
  version: "17"
  storageGiB: 32
  allowedCidrs:               # empty admits no one
    - 203.0.113.0/24
  protect: true               # deletion protection + final snapshot (AWS)</pre></div>
  <p class="note">On Azure the same ObjectStorage says <code>cloud: azure</code>, a <code>location</code>, and <code>emptyOnDelete: true</code>, which Azure requires because it deletes an account with its contents. It creates a resource group, a storage account and one private container, and consumers read the connection string from the <code>&lt;name&gt;-credentials</code> Secret.</p>
</section>

<section>
  <h2>What an app reads</h2>
  <div class="prose"><p>Two objects, with the same names on every kind, both in the XR's own namespace. The XR's <code>status</code> repeats the non-secret values.</p></div>
  <div class="cards">
    <div class="card"><span class="eyebrow">ConfigMap</span><h3>&lt;name&gt;-connection</h3><p>Everything that isn't secret, written by the composition. A queue's name and endpoint (plus its ARN, region and dead-letter URL on AWS); a bucket's name and endpoint; a database's host, port, database, username and <code>sslmode</code>.</p></div>
    <div class="card"><span class="eyebrow">Secret</span><h3>&lt;name&gt;-credentials</h3><p>Written by the cloud provider, never by the composition, and never in git. The database password, generated by the provider; on Azure, the queue's or account's connection string. On AWS a queue or bucket has no Secret at all: access is the consumer's role.</p></div>
  </div>
</section>

<section>
  <h2>DependencyReady, with a fixed set of reasons</h2>
  <div class="prose"><p>Each kind reports one condition of its own beside Crossplane's <code>Ready</code> and <code>Synced</code>. Each reason has exactly one meaning, so a script or an agent can branch on it.</p></div>
  <div class="tbl"><table>
    <thead><tr><th>Reason</th><th>State</th><th>Means</th></tr></thead>
    <tbody>{rrows}</tbody>
  </table></div>
  {fig2}
</section>

<section>
  <h2>What was verified</h2>
  <div class="prose"><p>On October 24, 2026, on the dev cluster against Hangar's AWS account, a throwaway Lambda target and one of each kind were requested through the tenants repo, checked, then removed the same way.</p></div>
  <div class="tbl"><table>
    <thead><tr><th>Check</th><th>Result</th><th>What I saw</th></tr></thead>
    <tbody>{crows}</tbody>
  </table></div>
</section>

<section>
  <h2>Limits to plan around</h2>
  <div class="prose"><p>Airframe's known gaps 8 to 10, written down rather than discovered later.</p></div>
  <div class="cards">
    <div class="card"><span class="eyebrow">Gap 8</span><h3>Lambda is the only consumer</h3><p>An ECS service has no task role for app code yet. A Kubernetes app has no cloud identity. Azure consumers use the connection string.</p></div>
    <div class="card"><span class="eyebrow">Gap 9</span><h3>The database is public-endpoint only</h3><p>A Lambda function outside a VPC has no fixed address, so reaching the database means <code>0.0.0.0/0</code>, with the password and TLS as the protection. There is no separate app role yet.</p></div>
    <div class="card"><span class="eyebrow">Gap 10</span><h3>Azure hasn't run</h3><p>The Azure compositions are render-tested and schema-checked, but their three providers aren't installed on the dev cluster yet.</p></div>
  </div>
</section>
""")
