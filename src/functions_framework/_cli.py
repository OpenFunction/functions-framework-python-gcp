# Copyright 2023 The OpenFunction Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import click

from functions_framework import _function_registry
from functions_framework.runner import Runner


@click.command()
@click.option("--target", envvar="FUNCTION_TARGET", type=click.STRING, required=True)
@click.option("--source", envvar="FUNCTION_SOURCE", type=click.Path(), default=None)
@click.option("--host", envvar="HOST", type=click.STRING, default="0.0.0.0")
@click.option("--port", envvar="PORT", type=click.INT, default=8080)
@click.option("--debug", envvar="DEBUG", is_flag=True)
@click.option("--dry-run", envvar="DRY_RUN", is_flag=True)
def _cli(target, source, host, port, debug, dry_run):
    # fetch the context
    context = _function_registry.get_openfunction_context('')

    runner = Runner(context, target, source, host, port, debug, dry_run)
    runner.run()


def run_dry(target, host, port):
    click.echo("Function: {}".format(target))
    click.echo("URL: http://{}:{}/".format(host, port))
    click.echo("Dry run successful, shutting down.")