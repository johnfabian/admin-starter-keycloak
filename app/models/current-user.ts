export interface CurrentUser {
  id: string;
  firstName: string;
  lastName: string;
  name: string;
  email: string;
  image?: string | null;
  roles: string[];
}
