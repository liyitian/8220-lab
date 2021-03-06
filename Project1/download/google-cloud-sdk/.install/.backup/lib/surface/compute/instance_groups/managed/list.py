# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Command for listing managed instance groups."""
from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import managed_instance_groups_utils
from googlecloudsdk.core import log


# TODO(user): This acts like
# instance-groups list --only-managed
# so they should share code.
class List(base_classes.ZonalLister,
           base_classes.InstanceGroupManagerDynamicProperiesMixin):
  """List Google Compute Engine managed instance groups."""

  @property
  def service(self):
    return self.compute.instanceGroupManagers

  @property
  def resource_type(self):
    return 'instanceGroupManagers'

  def GetResources(self, args, errors):
    resources = super(List, self).GetResources(args, errors)
    return [resource for resource in resources if resource.zone]

  def Display(self, args, resources):
    """Prints the given resources."""
    resources = list(resources)
    super(List, self).Display(args, resources)
    if self._AutoscalerWithErrorInList(resources):
      log.err.Print('(*) - there are errors in your autoscaling setup, please '
                    'describe the resource to see details')

  def ComputeDynamicProperties(self, args, items):
    """Add Autoscaler information if Autoscaler is defined for the item."""
    # Items are expected to be IGMs.
    for mig in managed_instance_groups_utils.AddAutoscalersToMigs(
        migs_iterator=self.ComputeInstanceGroupSize(items=items),
        project=self.project,
        compute=self.compute,
        http=self.http,
        batch_url=self.batch_url,
        fail_when_api_not_supported=False):
      if 'autoscaler' in mig and mig['autoscaler'] is not None:
        if (hasattr(mig['autoscaler'], 'status') and mig['autoscaler'].status ==
            self.messages.Autoscaler.StatusValueValuesEnum.ERROR):
          mig['autoscaled'] = 'yes (*)'
        else:
          mig['autoscaled'] = 'yes'
      else:
        mig['autoscaled'] = 'no'
      yield mig

  def _AutoscalerWithErrorInList(self, resources):
    for resource in resources:
      if resource['autoscaled'] == 'yes (*)':
        return True
    return False


List.detailed_help = base_classes.GetZonalListerHelp('managed instance groups')
