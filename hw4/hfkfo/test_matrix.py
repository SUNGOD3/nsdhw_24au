import _matrix
import pytest
import random
import unittest
import os
import timeit
import sys

class GradingTest(unittest.TestCase):

    def make_matrices(self, size):

        mat1 = _matrix.Matrix(size,size)
        mat2 = _matrix.Matrix(size,size)
        mat3 = _matrix.Matrix(size,size)

        for it in range(size):
            for jt in range(size):
                mat1[it, jt] = it * size + jt + 1
                mat2[it, jt] = it * size + jt + 1
                mat3[it, jt] = 0

        return mat1, mat2, mat3

    def test_basic(self):

        self.assertEqual(0, _matrix.bytes())

        size = 100
        mat1, mat2, mat3, *_ = self.make_matrices(size)
        self.assertEqual(3*8 * size*size, _matrix.bytes())
        base_alloc = _matrix.allocated()
        base_dealloc = _matrix.deallocated()

        self.assertEqual(size, mat1.nrow)
        self.assertEqual(size, mat1.ncol)
        self.assertEqual(size, mat2.nrow)
        self.assertEqual(size, mat2.ncol)
        self.assertEqual(size, mat3.nrow)
        self.assertEqual(size, mat3.ncol)

        self.assertEqual(2, mat1[0,1])
        self.assertEqual(size+2, mat1[1,1])
        self.assertEqual(size*2, mat1[1,size-1])
        self.assertEqual(size*size, mat1[size-1,size-1])

        for i in range(mat1.nrow):
            for j in range(mat1.ncol):
                self.assertNotEqual(0, mat1[i,j])
                self.assertEqual(mat1[i,j], mat2[i,j])
                self.assertEqual(0, mat3[i,j])

        self.assertEqual(mat1, mat2)
        self.assertTrue(mat1 is not mat2)

        self.assertEqual(3*8 * size*size, _matrix.bytes())
        self.assertEqual(base_alloc, _matrix.allocated())
        self.assertEqual(base_dealloc, _matrix.deallocated())

    def test_match_naive_mkl(self):

        self.assertEqual(0, _matrix.bytes())

        size = 100
        mat1, mat2, *_ = self.make_matrices(size)
        self.assertEqual(3*8 * size*size, _matrix.bytes())
        base_alloc = _matrix.allocated()
        base_dealloc = _matrix.deallocated()

        ret_naive = _matrix.multiply_naive(mat1, mat2)
        ret_mkl = _matrix.multiply_mkl(mat1, mat2)

        self.assertEqual(size, ret_naive.nrow)
        self.assertEqual(size, ret_naive.ncol)
        self.assertEqual(size, ret_mkl.nrow)
        self.assertEqual(size, ret_mkl.ncol)

        for i in range(ret_naive.nrow):
            for j in range(ret_naive.ncol):
                self.assertNotEqual(mat1[i,j], ret_mkl[i,j])
                self.assertEqual(ret_naive[i,j], ret_mkl[i,j])

        self.assertEqual(5*8 * size*size, _matrix.bytes())
        self.assertEqual(base_alloc + 2*8 * size*size, _matrix.allocated())
        self.assertEqual(base_dealloc, _matrix.deallocated())

    def test_zero(self):

        self.assertEqual(0, _matrix.bytes())

        size = 200
        mat1, mat2, mat3, *_ = self.make_matrices(size)
        self.assertEqual(3*8 * size*size, _matrix.bytes())
        base_alloc = _matrix.allocated()
        base_dealloc = _matrix.deallocated()

        ret_naive = _matrix.multiply_naive(mat1, mat3)
        ret_mkl = _matrix.multiply_mkl(mat1, mat3)

        self.assertEqual(size, ret_naive.nrow)
        self.assertEqual(size, ret_naive.ncol)
        self.assertEqual(size, ret_mkl.nrow)
        self.assertEqual(size, ret_mkl.ncol)

        for i in range(ret_naive.nrow):
            for j in range(ret_naive.ncol):
                self.assertEqual(0, ret_naive[i,j])
                self.assertEqual(0, ret_mkl[i,j])

        self.assertEqual(5*8 * size*size, _matrix.bytes())
        self.assertEqual(base_alloc + 2*8 * size*size, _matrix.allocated())
        self.assertEqual(base_dealloc, _matrix.deallocated())

    def test_memory(self):

        self.assertEqual(0, _matrix.bytes())
        base_alloc = _matrix.allocated()
        base_dealloc = _matrix.deallocated()

        size = 100
        mat1, mat2, mat3, *_ = self.make_matrices(size)
        self.assertEqual(3*8 * size*size, _matrix.bytes())
        # New allocation.
        self.assertEqual(base_alloc + 3*8 * size*size, _matrix.allocated())
        # No deallocation.
        self.assertEqual(base_dealloc, _matrix.deallocated())
        mat1 = mat2 = mat3 = None
        # Matrices are deallocated.
        self.assertEqual(0, _matrix.bytes())
        self.assertEqual(base_dealloc + 3*8 * size*size, _matrix.deallocated())
        self.assertEqual(base_alloc + 3*8 * size*size, _matrix.allocated())