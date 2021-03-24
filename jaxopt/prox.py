# Copyright 2021 Google LLC
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

"""Proximity operators."""

import jax
import jax.numpy as jnp

from jaxopt import tree_util


def prox_lasso(x, params, scaling=1.0):
  r"""Proximal operator for the l1 norm, i.e., soft-thresholding operator.

  The output is:
    argmin_y 0.5 ||y - x||^2 + scaling * params ||y||_1.
  When params is a pytree, the weights are applied coordinate-wise.

  Args:
    x: input pytree.
    params: regularization strength, float or pytree (same structure as x).
    scaling: a scaling factor.
  Returns:
    y: output pytree with same structure as x.
  """
  fun = lambda u, v: jnp.sign(u) * jax.nn.relu(jnp.abs(u) - v * scaling)
  return tree_util.tree_multimap(fun, x, params)


def prox_elastic_net(x, params, scaling=1.0):
  r"""Proximal operator for the elastic net.

  The output is:
    argmin_y 0.5 ||y - x||^2 + scaling * params[0] * g(y)

  where g(y) = ||y||_1 + params[1] * 0.5 * ||y||_2^2.

  Args:
    x: input pytree.
    params: a tuple, where both params[0] and params[1] can be either floats
      or pytrees with the same structure as x.
    scaling: a scaling factor.
  Returns:
    y: output pytree with same structure as x.
  """
  prox_l1 = lambda u, lam: jnp.sign(u) * jax.nn.relu(jnp.abs(u) - lam)
  fun = lambda u, lam, gamma: (prox_l1(u, scaling * lam) /
                               (1.0 + scaling * lam * gamma))
  return tree_util.tree_multimap(fun, x, params[0], params[1])