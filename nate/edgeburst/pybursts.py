"""
This is a MODULE docstring
"""
# modification of pybursts package by Renzo Poddighe: https://pypi.org/project/pybursts/
import numpy as np
import math
import numba
from numba import njit, jit


def single(offsets, s=2, gamma=1):
    """
	This is a docstring.
	"""
    if s <= 1:
        raise ValueError("s must be greater than 1!")
    if gamma <= 0:
        raise ValueError("gamma must be positive!")
    if len(offsets) < 1:
        raise ValueError("offsets must be non-empty!")

    offsets = np.array(offsets, dtype=object)

    if offsets.size == 1:
        bursts = np.array([0, offsets[0], offsets[0]], ndmin=2, dtype=object)
        return bursts

    offsets = np.sort(offsets)
    gaps = np.diff(offsets)

    if not np.all(gaps):
        raise ValueError("Input cannot contain events with zero time between!")

    T = np.sum(gaps)
    n = np.size(gaps)
    g_hat = T / n

    k = int(
        math.ceil(float(1 + math.log(T, s) + math.log(1 / np.amin(gaps), s))))

    gamma_log_n = gamma * math.log(n)

    alpha_function = np.vectorize(lambda x: s**x / g_hat)
    alpha = alpha_function(np.arange(k))

    C = np.repeat(float("inf"), k)

    C[0] = 0

    q = np.empty((k, 0))
    for t in range(n):
        C_prime = np.repeat(float("inf"), k)
        q_prime = np.empty((k, t + 1))
        q_prime.fill(np.nan)
        k_range = np.arange(0, k)
        C_temp = C[k_range]
        gaps_t = gaps[t]
        for j in range(k):
            tau_arr = tau(k_range, j, gamma_log_n)
            cost = np.add(C_temp, tau_arr)
            el = min_cost(cost)
            alpha_temp = alpha[j]
            f_j_t = f(alpha_temp, gaps_t)

            if f_j_t > 0:
                C_prime[j] = cost[el] - math.log(f_j_t)

            if t > 0:
                q_prime[j, :t] = q[el, :]

            q_prime[j, t] = j + 1

        C = C_prime
        q = q_prime

    j = np.argmin(C)
    q = q[j, :]

    prev_q = 0

    N = int(0)
    for t in range(n):
        if q[t] > prev_q:
            N = N + q[t] - prev_q
        prev_q = q[t]

    bursts = np.array([
        np.repeat(np.newaxis, N),
        np.repeat(offsets[0], N),
        np.repeat(offsets[0], N)
    ],
                      ndmin=2,
                      dtype=object).transpose()

    burst_counter = -1
    prev_q = 0
    stack = np.repeat(np.newaxis, N)
    stack_counter = -1
    for t in range(n):
        if q[t] > prev_q:
            num_levels_opened = q[t] - prev_q
            for i in range(int(num_levels_opened)):
                burst_counter += 1
                bursts[burst_counter, 0] = int(prev_q + i)
                bursts[burst_counter, 1] = offsets[t]
                stack_counter += 1
                stack[stack_counter] = burst_counter
        elif q[t] < prev_q:
            num_levels_closed = prev_q - q[t]
            for i in range(int(num_levels_closed)):
                bursts[stack[stack_counter], 2] = offsets[t]
                stack_counter -= 1
        prev_q = q[t]

    while stack_counter >= 0:
        bursts[stack[stack_counter], 2] = offsets[n]
        stack_counter -= 1

    burst_lists = []

    for burst in bursts:
        burst_lists.append(burst.tolist())

    return bursts


@njit
def f(alpha, x):
    """
	This is a docstring.
	"""
    return alpha * math.exp(-alpha * x)


@njit
def min_cost(cost):
    """
	This is a docstring.
	"""
    return np.argmin(cost)


@njit(cache=False)
def tau(i, j, gamma_log_n):
    """
	This is a docstring.
	"""
    return np.where(i >= j, 0, ((j - i) * gamma_log_n))


@jit(forceobj=True)
def process(offset_list, s, gamma):
    """
	This is a docstring.
	"""
    bursts = [single(x, s, gamma) for x in offset_list]
    return bursts
