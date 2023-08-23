# SETTING UP TO WORK WITH THIS FILE:
# -------------------------------------------------------------------------------
#
# The terraform state associated with this file is stored in a dedicated GCP
# bucket, so in order to work with this file you need to do the following after
# clearing a local .terraform folder.
#
# terraform init -backend-config backends/pangeo-backend.hcl
# terraform workspace list
# terraform workspace select <...>
#
# The GCP project having the bucket is https://console.cloud.google.com/?project=columbia
#

prefix                 = "pangeo-hubs"
project_id             = "pangeo-integration-te-3eea"
zone                   = "us-central1-b"
region                 = "us-central1"
core_node_machine_type = "n2-highmem-4"
enable_private_cluster = true

# Multi-tenant cluster, network policy is required to enforce separation between hubs
enable_network_policy = true

# Setup a filestore for in-cluster NFS
enable_filestore      = true
filestore_capacity_gb = 4096

regional_cluster = false


user_buckets = {
  "scratch-staging" : {
    "delete_after" : 7
  },
  "scratch" : {
    "delete_after" : 7
  },
  "coessing-scratch" : {
    "delete_after" : 14
  }
}

# Setup notebook node pools
notebook_nodes = {
  "small" : {
    min : 0,
    max : 100,
    machine_type : "n1-standard-2",
    labels : {},
    gpu : {
      enabled : false,
      type : "",
      count : 0
    }
  },
  "medium" : {
    min : 0,
    max : 100,
    machine_type : "n1-standard-4",
    labels : {},
    gpu : {
      enabled : false,
      type : "",
      count : 0
    }
  },
  "large" : {
    min : 0,
    max : 100,
    machine_type : "n1-standard-8",
    labels : {},
    gpu : {
      enabled : false,
      type : "",
      count : 0
    }
  },
  "huge" : {
    min : 0,
    max : 100,
    machine_type : "n1-standard-16",
    labels : {},
    gpu : {
      enabled : false,
      type : "",
      count : 0
    }
  },
}

# Setup a single node pool for dask workers.
#
# A not yet fully established policy is being developed about using a single
# node pool, see https://github.com/2i2c-org/infrastructure/issues/2687.
#
# TODO: Transition to a single n2-highmem-16 worker node pool to be able to
#       provide standardized worker pod config for all daskhubs.
#
#       Tracked in https://github.com/2i2c-org/infrastructure/issues/2687
#
#       The node pool to setup should look like this:
#
#       "worker" : {
#         min : 0,
#         max : 100,
#         machine_type : "n2-highmem-16",
#       },
#
dask_nodes = {
  "small" : {
    min : 0,
    max : 100,
    machine_type : "n1-standard-4",
    labels : {},
    gpu : {
      enabled : false,
      type : "",
      count : 0
    }
  },
  "medium" : {
    min : 0,
    max : 100,
    machine_type : "n1-standard-8",
    labels : {},
    gpu : {
      enabled : false,
      type : "",
      count : 0
    }
  },
  "large" : {
    min : 0,
    max : 100,
    machine_type : "n1-standard-16",
    labels : {},
    gpu : {
      enabled : false,
      type : "",
      count : 0
    }
  },
}

hub_cloud_permissions = {
  "staging" : {
    requestor_pays : true,
    bucket_admin_access : ["scratch-staging"],
    hub_namespace : "staging"
  },
  "prod" : {
    requestor_pays : true,
    bucket_admin_access : ["scratch"],
    hub_namespace : "prod"
  },
  "coessing" : {
    requestor_pays : true,
    bucket_admin_access : ["coessing-scratch"],
    hub_namespace : "coessing"
  },
}
