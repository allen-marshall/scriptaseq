"""Unit tests for functionality in the scriptaseq.internal.mime_data module."""

from unittest import TestCase

from scriptaseq.internal.project_tree.project_tree_nodes import DirProjectTreeNode, SequenceProjectTreeNode
from scriptaseq.internal.mime_data import encode_project_tree_node_path, decode_project_tree_node_path
from scriptaseq.named_tree_node import TreeNamePath


class ProjectTreeNodePathMediaTypeTest(TestCase):
  """Unit tests for encoding and decoding of project tree node paths."""
  
  def test_encode_success(self):
    # Test that project tree node paths encode to the expected values.
    
    data = encode_project_tree_node_path(TreeNamePath.from_str('/'))
    self.assertEqual(data.decode('utf-8'), '/')
    
    data = encode_project_tree_node_path(TreeNamePath.from_str('/childDir0'))
    self.assertEqual(data.decode('utf-8'), '/childDir0')
    
    data = encode_project_tree_node_path(TreeNamePath.from_str('/childDir1'))
    self.assertEqual(data.decode('utf-8'), '/childDir1')
    
    data = encode_project_tree_node_path(TreeNamePath.from_str('/childDir0/grandchildSeq'))
    self.assertEqual(data.decode('utf-8'), '/childDir0/grandchildSeq')
  
  def test_encode_fail(self):
    # Test that project tree node path encoding fails when expected.
    self.assertRaises(ValueError, encode_project_tree_node_path, TreeNamePath.from_str('abc/def'))
    self.assertRaises(ValueError, encode_project_tree_node_path, TreeNamePath.from_str(''))
  
  def test_decode_success(self):
    # Test that encoded project tree node paths decode to the expected values.
    
    path = TreeNamePath.from_str('/abc/def')
    decoded_path = decode_project_tree_node_path(str(path).encode('utf-8'))
    self.assertEqual(path, decoded_path)
    
    path = TreeNamePath.from_str('/')
    decoded_path = decode_project_tree_node_path(str(path).encode('utf-8'))
    self.assertEqual(path, decoded_path)
  
  def test_decode_fail(self):
    # Test that project tree node path decoding fails when expected.
    self.assertRaises(ValueError, decode_project_tree_node_path, 'abc/def'.encode('utf-8'))
    self.assertRaises(ValueError, decode_project_tree_node_path, ''.encode('utf-8'))