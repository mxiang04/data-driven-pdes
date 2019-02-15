# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Test for create_training_data."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path

from absl import flags
from absl.testing import flagsaver
from absl.testing import parameterized
from pde_superresolution_2d.core import builders
from pde_superresolution_2d.pipelines import create_training_data
from tensorflow import gfile
from absl.testing import absltest

FLAGS = flags.FLAGS

EQUATION_KWARGS = {
    'advection_diffusion': {
        'diffusion_coefficient': 0.005,
        'cfl_safety_factor': 0.9,
    },
    'saint_venant': {},
}


class CreateTrainingDataTest(parameterized.TestCase):

  @parameterized.parameters(*((equation_name, dataset_type)
                              for dataset_type in builders.DATASET_TYPES
                              for equation_name in EQUATION_KWARGS))
  def test(self, equation_name, dataset_type):
    output_path = FLAGS.test_tmpdir
    output_name = 'temp'
    shards = 1

    # run the beam job
    with flagsaver.flagsaver(
        dataset_path=output_path,
        dataset_name=output_name,
        dataset_type=dataset_type,
        equation_name=equation_name,
        equation_kwargs=str(EQUATION_KWARGS[equation_name]),
        num_shards=shards,
        total_time_steps=10,
        example_time_steps=3,
        time_step_interval=5,
        num_seeds=2):
      create_training_data.main([])

    # verify that file was written
    data_path = os.path.join(output_path,
                             output_name + '.tfrecord-00000-of-0000%i' % shards)
    metadata_path = os.path.join(output_path, output_name + '.metadata')
    self.assertTrue(gfile.Exists(data_path))
    self.assertTrue(gfile.Exists(metadata_path))


if __name__ == '__main__':
  absltest.main()