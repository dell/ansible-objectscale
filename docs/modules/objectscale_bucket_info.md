# dellemc.objectscale.objectscale_bucket_info

**Retrieve information about ObjectScale buckets**

## Synopsis

- Retrieves details of one or more ObjectScale buckets.

## Parameters

| Parameter              | Comments                                                                 |
| ---------------------- | ------------------------------------------------------------------------ |
| `objectscale_host`     | FQDN or IP address of the ObjectScale management endpoint. (Required)    |
| `objectscale_username` | Username for authentication. (Required)                                  |
| `objectscale_password` | Password for authentication. (Required, no_log)                          |
| `validate_certs`       | Whether to validate SSL certificates. (bool, default: true)              |
| `namespace`            | The ObjectScale namespace where the bucket resides. (Required)           |
| `name`                 | The name of the bucket to retrieve. If omitted, no buckets are returned. |

## Examples

```yaml
- name: Get info for a single bucket
  dellemc.objectscale.objectscale_bucket_info:
    objectscale_host: "{{ os_host }}"
    objectscale_username: "{{ os_user }}"
    objectscale_password: "{{ os_pass }}"
    validate_certs: false
    namespace: "my-namespace"
    name: "my-bucket"
```

## Return Values

| Key       | Description                               |
| --------- | ----------------------------------------- |
| `buckets` | A list of buckets with their details. (list) |
