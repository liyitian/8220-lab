# Copyright 2013 Google Inc. All Rights Reserved.
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

"""Command to set properties."""

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exc
from googlecloudsdk.core import log
from googlecloudsdk.core import named_configs
from googlecloudsdk.core import properties
from googlecloudsdk.core import remote_completion


DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """\
        To set the project property in the core section, run:

          $ {command} project myProject

        To set the zone property in the compute section, run:

          $ {command} compute/zone zone3
        """,
    '+AVAILABLE PROPERTIES': properties.VALUES.GetHelpString(),
}


class Set(base.Command):
  """Edit Google Cloud SDK properties.

  Set the value for an option, so that Cloud SDK tools can use them as
  configuration.
  """

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Adds args for this command."""
    property_arg = parser.add_argument(
        'property',
        metavar='SECTION/PROPERTY',
        help='The property to be set. Note that SECTION/ is optional while '
        'referring to properties in the core section.')
    property_arg.completer = Set.group_class.PropertiesCompleter
    value_arg = parser.add_argument(
        'value',
        completion_resource='cloudresourcemanager.projects',
        list_command_path='beta.projects',
        help='The value to be set.')
    value_arg.completer = Set.ValueCompleter

    scope_args = parser.add_mutually_exclusive_group()
    Set.group_class.DEPRECATED_SCOPE_FLAG.AddToParser(scope_args)
    Set.group_class.INSTALLATION_FLAG.AddToParser(scope_args)

  @staticmethod
  def ValueCompleter(prefix, parsed_args, **unused_kwargs):
    prop = properties.FromString(getattr(parsed_args, 'property'))
    if not prop:
      # No property was given, or it was invalid.
      return

    if prop.choices:
      return [c for c in prop.choices if c.startswith(prefix)]

    if not prop.resource:
      # No collection associated with the property.
      return
    cli_generator = Set.GetCLIGenerator()
    if not cli_generator:
      return

    completer = remote_completion.RemoteCompletion.GetCompleterForResource(
        prop.resource, cli_generator, command_line=prop.resource_command_path)
    return completer(prefix=prefix, parsed_args=parsed_args, **unused_kwargs)

  def Run(self, args):
    if args.scope:
      log.err.Print('The `--scope` flag is deprecated.  Please run `gcloud '
                    'help topic configurations` and `gcloud help config set` '
                    'for more information.')

    requested_scope = Set.group_class.RequestedScope(args)

    if not requested_scope:
      named_configs.TryEnsureWriteableNamedConfig()

    prop = properties.FromString(args.property)
    if not prop:
      raise c_exc.InvalidArgumentException(
          'property', 'Must be in the form: [SECTION/]PROPERTY')
    properties.PersistProperty(prop, args.value, scope=requested_scope)



