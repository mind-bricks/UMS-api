from os import path

from rest_framework import (
    reverse,
    status,
    test,
)


class UserPreLoginTest(test.APITestCase):
    def test_signup_user(self):
        pass


class UserPostLoginTest(test.APITestCase):
    fixtures = [
        path.join('fixtures', 'users.json'),
        path.join('fixtures', 'test_users.json'),
    ]

    def setUp(self):
        url_login = reverse.reverse('users:users-login')
        response = self.client.post(url_login, data={
            'username': 'test_user',
            'password': 'abcdefgh',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('expires_in', response.data)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(
            response.data.get('access_token')))

    def test_change_user_password(self):
        url_password = reverse.reverse('users:users-password')
        url_login = reverse.reverse('users:users-login')
        response = self.client.post(url_password, data={
            'password': '111111',
            'password_new': '123456789',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(url_password, data={
            'password': 'abcdefgh',
            'password_new': '123456789',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials()
        response = self.client.post(url_login, data={
            'username': 'test_user',
            'password': '123456789',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user_self(self):
        url_self = reverse.reverse('users:users-self')
        response = self.client.get(url_self)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('username'), 'test_user')

    def test_update_user_self(self):
        url_self = reverse.reverse('users:users-self')
        response = self.client.patch(url_self, data={
            'first_name': 'new first name',
            'last_name': 'new last name',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('first_name'), 'new first name')
        self.assertEqual(response.data.get('last_name'), 'new last name')

    def test_list_user_self_group(self):
        url_self = reverse.reverse('users:users-self-groups')
        response = self.client.get(url_self)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

    def test_list_user_self_permission(self):
        url_self = reverse.reverse('users:users-self-permissions')
        response = self.client.get(url_self)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)


class AdminTest(test.APITestCase):
    access_token_of_admin = None
    access_token_of_user = None
    fixtures = [
        path.join('fixtures', 'users.json'),
        path.join('fixtures', 'test_users.json'),
    ]

    @classmethod
    def setUpTestData(cls):
        url_login = reverse.reverse('users:users-login')
        client = cls.client_class()
        response = client.post(url_login, data={
            'username': 'test_admin',
            'password': 'abcdefgh',
        })
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertIn('access_token', response.data)
        # self.assertIn('refresh_token', response.data)
        # self.assertIn('expires_in', response.data)
        cls.access_token_of_admin = response.data.get('access_token')

        response = client.post(url_login, data={
            'username': 'test_user',
            'password': 'abcdefgh',
        })
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertIn('access_token', response.data)
        # self.assertIn('refresh_token', response.data)
        # self.assertIn('expires_in', response.data)
        cls.access_token_of_user = response.data.get('access_token')


class UserAdminTest(AdminTest):

    def test_signup_user(self):
        url_signup = reverse.reverse('users:users-signup')
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.post(url_signup, data={
            'username': 'test_user_tmp',
            'password': '1234567',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.post(url_signup, data={
            'username': 'test_user_tmp',
            'password': '1234567',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('realm'), '')
        self.assertEqual(response.data.get('username'), 'test_user_tmp')
        self.assertNotIn('password', response.data)

    def test_list_user(self):
        url_list = reverse.reverse('users:users-list')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 3)

    def test_retrieve_user(self):
        url_detail = reverse.reverse(
            'users:users-detail', ['dc9b60b8-3115-11ea-bbc8-a86bad54c153'])

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('username'), 'test_admin')
        self.assertEqual(response.data.get('first_name'), 'admin_first_name')
        self.assertEqual(response.data.get('last_name'), 'admin_last_name')


class GroupAdminTest(AdminTest):
    def test_list_group(self):
        url_list = reverse.reverse('users:groups-list')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 3)

    def test_create_group(self):
        url_list = reverse.reverse('users:groups-list')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.post(url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.post(url_list, data={'name': 'test_group_2'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(url_list, data={'name': 'test_group_2'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy_group(self):
        url_detail_1 = reverse.reverse('users:groups-detail', ['test_group'])
        url_detail_2 = reverse.reverse('users:groups-detail', ['superuser'])
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.delete(url_detail_1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.delete(url_detail_1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(url_detail_2)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_list_user_group(self):
        url_list = reverse.reverse('users:user-groups-list', [
            'cd927db8-3115-11ea-bbc8-a86bad54c153'])
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

    def test_create_user_group(self):
        url_list = reverse.reverse('users:user-groups-list', [
            'cd927db8-3115-11ea-bbc8-a86bad54c153'])
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.post(
            url_list, data={'name': 'test_group'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.post(
            url_list, data={'name': 'test_group'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(
            url_list, data={'name': 'test_group_not_existing'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

    def test_destroy_user_group(self):
        url_detail = reverse.reverse('users:user-groups-detail', [
            'cd927db8-3115-11ea-bbc8-a86bad54c153',
            'test_group_1'
        ])
        url_list = reverse.reverse('users:user-groups-list', [
            'cd927db8-3115-11ea-bbc8-a86bad54c153'
        ])
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 0)


class PermissionAdminTest(AdminTest):
    def test_list_permission(self):
        url_list = reverse.reverse('users:permissions-list')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 13)

    def test_create_permission(self):
        url_list = reverse.reverse('users:permissions-list')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.post(url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.post(
            url_list, data={'name': 'tmp.permission'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(
            url_list, data={'name': 'tmp.permission'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy_permission(self):
        url_detail_1 = reverse.reverse(
            'users:permissions-detail', ['test.permission'])
        url_detail_2 = reverse.reverse(
            'users:permissions-detail', ['users.admin'])
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.delete(url_detail_1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.delete(url_detail_1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(url_detail_2)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_list_user_permission(self):
        url_list = reverse.reverse('users:user-permissions-list', [
            'cd927db8-3115-11ea-bbc8-a86bad54c153'])
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

    def test_create_user_permission(self):
        url_list = reverse.reverse('users:user-permissions-list', [
            'cd927db8-3115-11ea-bbc8-a86bad54c153'])
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.post(
            url_list, data={'name': 'test.permission'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.post(
            url_list, data={'name': 'test.permission'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(
            url_list, data={'name': 'test.permission_not_existing'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

    def test_destroy_user_permission(self):
        url_detail = reverse.reverse('users:user-permissions-detail', [
            'cd927db8-3115-11ea-bbc8-a86bad54c153',
            'test.permission_1'
        ])
        url_list = reverse.reverse('users:user-permissions-list', [
            'cd927db8-3115-11ea-bbc8-a86bad54c153'
        ])
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 0)

    def test_list_group_permission(self):
        url_list = reverse.reverse(
            'users:group-permissions-list', ['test_group_1'])
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

    def test_create_group_permission(self):
        url_list = reverse.reverse(
            'users:group-permissions-list', ['test_group_1'])
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.post(
            url_list, data={'name': 'test.permission'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.post(
            url_list, data={'name': 'test.permission'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(
            url_list, data={'name': 'test.permission_not_existing'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

    def test_destroy_group_permission(self):
        url_detail = reverse.reverse('users:group-permissions-detail', [
            'test_group_1',
            'test.permission_2'
        ])
        url_list = reverse.reverse('users:group-permissions-list', [
            'test_group_1'
        ])
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 0)
