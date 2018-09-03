"""Unit tests for functionality in the scriptaseq.named_tree_node module."""

from unittest import TestCase

from scriptaseq.named_tree_node import TreeNamePath, NamedTreeNode


class TreeNamePathTest(TestCase):
  """Unit tests for the TreeNamePath class."""
  
  def test_is_absolute(self):
    # Test the is_absolute property using empty paths.
    
    path = TreeNamePath([])
    self.assertTrue(path.is_absolute)
    
    path = TreeNamePath([], True)
    self.assertTrue(path.is_absolute)
    
    path = TreeNamePath([], False)
    self.assertFalse(path.is_absolute)
    
    # Test the is_absolute property using nonempty paths.
    
    path_list = ['name0', 'name1', 'name2']
    
    path = TreeNamePath(path_list)
    self.assertTrue(path.is_absolute)
    
    path = TreeNamePath(path_list, True)
    self.assertTrue(path.is_absolute)
    
    path = TreeNamePath(path_list, False)
    self.assertFalse(path.is_absolute)
  
  def test_path_names(self):
    # Test the path_names property.
    
    path = TreeNamePath([])
    self.assertSequenceEqual(path.path_names, [])
    
    path_list = ['abc', 'def', 'ghi']
    
    path = TreeNamePath(path_list)
    self.assertSequenceEqual(path.path_names, path_list)
    
    path = TreeNamePath(path_list, False)
    self.assertSequenceEqual(path.path_names, path_list)
  
  def test_immutable(self):
    # Test immutability of sequence returned by path_names property.
    
    path = TreeNamePath(['first', 'second'])
    path_names = path.path_names
    def mutate():
      path_names[0] = 'ABCD'
    self.assertRaises(BaseException, mutate)
  
  def test_str(self):
    # Test conversion from TreeNamePath to string.
    
    path = TreeNamePath([])
    self.assertEqual(str(path), '/')
    
    path = TreeNamePath([], False)
    self.assertEqual(str(path), '')
    
    path_list = ['123', '456', '7890']
    
    path = TreeNamePath(path_list)
    self.assertEqual(str(path), '/123/456/7890')
    
    path = TreeNamePath(path_list, False)
    self.assertEqual(str(path), '123/456/7890')

class NamedTreeNodeTest(TestCase):
  """Unit tests for the NamedTreeNode class."""
  
  def setUp(self):
    self._tree_1node = NamedTreeNode('root123')
    
    self._tree_4node_root = NamedTreeNode('rootabc')
    self._tree_4node_child0 = NamedTreeNode('child0def', parent=self._tree_4node_root)
    self._tree_4node_child1 = NamedTreeNode('child1ghi', can_have_children=False, parent=self._tree_4node_root)
    self._tree_4node_grandchild = NamedTreeNode('grandchildjkl', parent=self._tree_4node_child0)
  
  def test_verify_name_valid(self):
    NamedTreeNode.verify_name_valid('abc')
    self.assertRaises(ValueError, NamedTreeNode.verify_name_valid, '')
    self.assertRaises(ValueError, NamedTreeNode.verify_name_valid, 'abc/')
  
  def test_verify_child_name_available(self):
    self._tree_1node.verify_child_name_available('abc')
    self._tree_4node_root.verify_child_name_available('child2mno')
    self.assertRaises(ValueError, self._tree_4node_child1.verify_child_name_available, 'abc')
    self.assertRaises(ValueError, self._tree_4node_root.verify_child_name_available, 'child0def')
    self.assertRaises(ValueError, self._tree_4node_root.verify_child_name_available, 'child1ghi')
    self.assertRaises(ValueError, self._tree_4node_child0.verify_child_name_available, 'grandchildjkl')
  
  def test_verify_can_add_as_child(self):
    self._tree_1node.verify_can_add_as_child(self._tree_4node_root)
    self._tree_4node_root.verify_can_add_as_child(self._tree_4node_child0)
    self._tree_4node_root.verify_can_add_as_child(self._tree_4node_grandchild)
    self.assertRaises(ValueError, self._tree_4node_root.verify_can_add_as_child, self._tree_4node_root)
    self.assertRaises(ValueError, self._tree_4node_child0.verify_can_add_as_child, self._tree_4node_root)
    self.assertRaises(ValueError, self._tree_4node_grandchild.verify_can_add_as_child, self._tree_4node_root)
    self.assertRaises(ValueError, self._tree_4node_child1.verify_can_add_as_child, self._tree_1node)
    child0_duplicate_named_node = NamedTreeNode('child0def')
    self.assertRaises(ValueError, self._tree_4node_root.verify_can_add_as_child, child0_duplicate_named_node)
  
  def test_children_retrieval(self):
    self.assertSequenceEqual(self._tree_1node.children.items(), [])
    self.assertSequenceEqual(self._tree_4node_root.children.items(),
      [('child0def', self._tree_4node_child0), ('child1ghi', self._tree_4node_child1)])
    self.assertSequenceEqual(self._tree_4node_child0.children.items(), [('grandchildjkl', self._tree_4node_grandchild)])
    self.assertSequenceEqual(self._tree_4node_child1.children.items(), [])
    self.assertSequenceEqual(self._tree_4node_grandchild.children.items(), [])
  
  def test_name_retrieval(self):
    self.assertEqual(self._tree_1node.name, 'root123')
    self.assertEqual(self._tree_4node_root.name, 'rootabc')
    self.assertEqual(self._tree_4node_child0.name, 'child0def')
    self.assertEqual(self._tree_4node_child1.name, 'child1ghi')
    self.assertEqual(self._tree_4node_grandchild.name, 'grandchildjkl')
    
  def test_name_assignment_success(self):
    self._tree_1node.name = 'root456'
    self.assertEqual(self._tree_1node.name, 'root456')
    self._tree_4node_grandchild.name = 'grandchildmno'
    self.assertEqual(self._tree_4node_grandchild.name, 'grandchildmno')
    self.assertSequenceEqual(self._tree_4node_child0.children.items(), [('grandchildmno', self._tree_4node_grandchild)])
    
  def test_name_assignment_fail(self):
    def set_name(node, name):
      node.name = name
    self.assertRaises(ValueError, set_name, self._tree_1node, 'root/456')
    self.assertRaises(ValueError, set_name, self._tree_1node, '')
    self.assertRaises(ValueError, set_name, self._tree_4node_root, 'root/')
    self.assertRaises(ValueError, set_name, self._tree_4node_child0, 'child1ghi')
  
  def test_parent_retrieval(self):
    self.assertIsNone(self._tree_1node.parent)
    self.assertIsNone(self._tree_4node_root.parent)
    self.assertIs(self._tree_4node_child0.parent, self._tree_4node_root)
    self.assertIs(self._tree_4node_child1.parent, self._tree_4node_root)
    self.assertIs(self._tree_4node_grandchild.parent, self._tree_4node_child0)
    
  def test_parent_assignment_success(self):
    self._tree_4node_grandchild.parent = self._tree_4node_root
    self.assertIs(self._tree_4node_grandchild.parent, self._tree_4node_root)
    self.assertSequenceEqual(self._tree_4node_root.children.items(),
      [('child0def', self._tree_4node_child0), ('child1ghi', self._tree_4node_child1),
      ('grandchildjkl', self._tree_4node_grandchild)])
    self._tree_4node_grandchild.parent = None
    self.assertIsNone(self._tree_4node_grandchild.parent)
    self.assertSequenceEqual(self._tree_4node_root.children.items(),
      [('child0def', self._tree_4node_child0), ('child1ghi', self._tree_4node_child1)])
    
  def test_parent_assignment_fail(self):
    def set_parent(node, parent):
      node.parent = parent
    self.assertRaises(ValueError, set_parent, self._tree_1node, self._tree_1node)
    self.assertRaises(ValueError, set_parent, self._tree_4node_root, self._tree_4node_root)
    self.assertRaises(ValueError, set_parent, self._tree_4node_root, self._tree_4node_child0)
    self.assertRaises(ValueError, set_parent, self._tree_4node_grandchild, self._tree_4node_child1)
    self._tree_4node_grandchild.name = 'child1ghi'
    self.assertRaises(ValueError, set_parent, self._tree_4node_root, self._tree_4node_grandchild)
  
  def test_can_have_children_retrieval(self):
    self.assertTrue(self._tree_1node.can_have_children)
    self.assertTrue(self._tree_4node_root.can_have_children)
    self.assertTrue(self._tree_4node_child0.can_have_children)
    self.assertFalse(self._tree_4node_child1.can_have_children)
    self.assertTrue(self._tree_4node_grandchild.can_have_children)
  
  def test_can_have_children_assignment(self):
    self._tree_1node.can_have_children = False
    self.assertFalse(self._tree_1node.can_have_children)
    
    self._tree_4node_child1.can_have_children = True
    self.assertTrue(self._tree_4node_child1.can_have_children)
    
    # Verify that setting can_have_children to false removes children.
    self._tree_4node_root.can_have_children = False
    self.assertEqual(len(self._tree_4node_root.children), 0)
    self.assertSequenceEqual(self._tree_4node_root.children.items(), [])
    self.assertIsNone(self._tree_4node_child0.parent)
    self.assertIsNone(self._tree_4node_child1.parent)
  
  def test_ancestors_retrieval(self):
    self.assertSequenceEqual(list(self._tree_1node.ancestors), [])
    self.assertSequenceEqual(list(self._tree_4node_root.ancestors), [])
    self.assertSequenceEqual(list(self._tree_4node_child0.ancestors), [self._tree_4node_root])
    self.assertSequenceEqual(list(self._tree_4node_child1.ancestors), [self._tree_4node_root])
    self.assertSequenceEqual(list(self._tree_4node_grandchild.ancestors),
      [self._tree_4node_child0, self._tree_4node_root])
  
  def test_tree_root_retrieval(self):
    self.assertIs(self._tree_1node.tree_root, self._tree_1node)
    self.assertIs(self._tree_4node_root.tree_root, self._tree_4node_root)
    self.assertIs(self._tree_4node_child0.tree_root, self._tree_4node_root)
    self.assertIs(self._tree_4node_child1.tree_root, self._tree_4node_root)
    self.assertIs(self._tree_4node_grandchild.tree_root, self._tree_4node_root)
  
  def test_abs_name_path_retrieval(self):
    path = self._tree_1node.abs_name_path
    self.assertTrue(path.is_absolute)
    self.assertSequenceEqual(path.path_names, [])
    
    path = self._tree_4node_root.abs_name_path
    self.assertTrue(path.is_absolute)
    self.assertSequenceEqual(path.path_names, [])
    
    path = self._tree_4node_child0.abs_name_path
    self.assertTrue(path.is_absolute)
    self.assertSequenceEqual(path.path_names, ['child0def'])
    
    path = self._tree_4node_child1.abs_name_path
    self.assertTrue(path.is_absolute)
    self.assertSequenceEqual(path.path_names, ['child1ghi'])
    
    path = self._tree_4node_grandchild.abs_name_path
    self.assertTrue(path.is_absolute)
    self.assertSequenceEqual(path.path_names, ['child0def', 'grandchildjkl'])
  
  def test_add_child_success(self):
    self._tree_4node_root.add_child(self._tree_4node_grandchild)
    self.assertIs(self._tree_4node_grandchild.parent, self._tree_4node_root)
    self.assertSequenceEqual(self._tree_4node_root.children.items(),
      [('child0def', self._tree_4node_child0), ('child1ghi', self._tree_4node_child1),
      ('grandchildjkl', self._tree_4node_grandchild)])
    
  def test_add_child_fail(self):
    def add_child(node, parent):
      parent.add_child(node)
    self.assertRaises(ValueError, add_child, self._tree_1node, self._tree_1node)
    self.assertRaises(ValueError, add_child, self._tree_4node_root, self._tree_4node_root)
    self.assertRaises(ValueError, add_child, self._tree_4node_root, self._tree_4node_child0)
    self.assertRaises(ValueError, add_child, self._tree_4node_grandchild, self._tree_4node_child1)
    self._tree_4node_grandchild.name = 'child1ghi'
    self.assertRaises(ValueError, add_child, self._tree_4node_root, self._tree_4node_grandchild)
  
  def test_remove_child(self):
    self._tree_4node_child0.remove_child(self._tree_4node_grandchild.name)
    self.assertIsNone(self._tree_4node_grandchild.parent)
    self.assertSequenceEqual(self._tree_4node_child0.children.items(), [])
    
    # Make sure removing a non-present child doesn't raise an exception.
    self._tree_1node.remove_child('nobody')
  
  def test_suggest_child_name_success(self):
    self.assertEqual(self._tree_4node_root.suggest_child_name('abc'), 'abc')
    self.assertEqual(self._tree_4node_root.suggest_child_name('child0def'), 'child0def00000000')
    NamedTreeNode('child0def00000000', parent=self._tree_4node_root)
    self.assertEqual(self._tree_4node_root.suggest_child_name('child0def'), 'child0def00000001')
  
  def test_suggest_child_name_fail(self):
    self.assertRaises(ValueError, self._tree_4node_root.suggest_child_name, '')
    self.assertRaises(ValueError, self._tree_4node_root.suggest_child_name, 'abc/')
    self.assertRaises(ValueError, self._tree_4node_child1.suggest_child_name, 'abc')
  
  def test_resolve_path_absolute_success(self):
    path = self._tree_1node.abs_name_path
    self.assertIs(self._tree_1node.resolve_path(path), self._tree_1node)
    
    path = self._tree_4node_grandchild.abs_name_path
    self.assertIs(self._tree_4node_root.resolve_path(path), self._tree_4node_grandchild)
    self.assertIs(self._tree_4node_child0.resolve_path(path), self._tree_4node_grandchild)
    self.assertIs(self._tree_4node_child1.resolve_path(path), self._tree_4node_grandchild)
    self.assertIs(self._tree_4node_grandchild.resolve_path(path), self._tree_4node_grandchild)
  
  def test_resolve_path_absolute_fail(self):
    path = TreeNamePath(['child1ghi', 'grandchildjkl'])
    def resolve(node):
      node.resolve_path(path)
    self.assertRaises(ValueError, resolve, self._tree_1node)
    self.assertRaises(ValueError, resolve, self._tree_4node_root)
    self.assertRaises(ValueError, resolve, self._tree_4node_child0)
    self.assertRaises(ValueError, resolve, self._tree_4node_child1)
    self.assertRaises(ValueError, resolve, self._tree_4node_grandchild)
  
  def test_resolve_path_relative_success(self):
    path = TreeNamePath(['grandchildjkl'], False)
    self.assertIs(self._tree_4node_child0.resolve_path(path), self._tree_4node_grandchild)
    
    # Add another node so we can test multi-level relative paths.
    great_grandchild = NamedTreeNode('greatgrandchildmno', parent=self._tree_4node_grandchild)
    path = TreeNamePath(['grandchildjkl', 'greatgrandchildmno'], False)
    self.assertIs(self._tree_4node_child0.resolve_path(path), great_grandchild)
  
  def test_resolve_path_relative_fail(self):
    path = TreeNamePath(['grandchildjkl'], False)
    def resolve(node):
      node.resolve_path(path)
    self.assertRaises(ValueError, resolve, self._tree_1node)
    self.assertRaises(ValueError, resolve, self._tree_4node_root)
    self.assertRaises(ValueError, resolve, self._tree_4node_child1)
    self.assertRaises(ValueError, resolve, self._tree_4node_grandchild)
  
  def test_idx_in_parent(self):
    self.assertIsNone(self._tree_1node.idx_in_parent())
    self.assertIsNone(self._tree_4node_root.idx_in_parent())
    self.assertEqual(self._tree_4node_child0.idx_in_parent(), 0)
    self.assertEqual(self._tree_4node_child1.idx_in_parent(), 1)
    self.assertEqual(self._tree_4node_grandchild.idx_in_parent(), 0)
  
  def test_child_at_idx_success(self):
    self.assertIs(self._tree_4node_root.child_at_idx(0), self._tree_4node_child0)
    self.assertIs(self._tree_4node_root.child_at_idx(1), self._tree_4node_child1)
    self.assertIs(self._tree_4node_root.child_at_idx(-1), self._tree_4node_child1)
    self.assertIs(self._tree_4node_root.child_at_idx(-2), self._tree_4node_child0)
  
  def test_child_at_idx_fail(self):
    def find_child(parent, idx):
      parent.child_at_idx(idx)
    self.assertRaises(IndexError, find_child, self._tree_1node, 0)
    self.assertRaises(IndexError, find_child, self._tree_4node_root, 2)
    self.assertRaises(IndexError, find_child, self._tree_4node_root, -3)
  
  def test_child_idx_from_name(self):
    self.assertEqual(self._tree_1node.child_idx_from_name('nobody'), 0)
    self.assertEqual(self._tree_4node_root.child_idx_from_name('child0def'), 0)
    self.assertEqual(self._tree_4node_root.child_idx_from_name('child1ghi'), 1)
    self.assertEqual(self._tree_4node_root.child_idx_from_name('child0deff'), 1)
  
  def test_sorting(self):
    middle_child = NamedTreeNode('child0defghi', parent=self._tree_4node_root)
    self.assertSequenceEqual(self._tree_4node_root.children.items(),
      [('child0def', self._tree_4node_child0), ('child0defghi', middle_child), ('child1ghi', self._tree_4node_child1)])