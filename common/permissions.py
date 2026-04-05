from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    message = "У вас нет прав для выполнения этого действия. Только модератор может выполнять операции с продуктами."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not request.user.is_staff:
            return False
        
        if request.method == 'POST':
            self.message = "Модератор не может создавать продукты (POST запрещён)."
            return False
        
        if request.method in permissions.SAFE_METHODS or request.method in ['PUT', 'PATCH', 'DELETE']:
            return True
        
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not request.user.is_staff:
            return False
        
        if request.method == 'DELETE' and obj.owner == request.user:
            self.message = "Вы не можете удалить свой собственный продукт."
            return False
        
        if request.method in permissions.SAFE_METHODS or request.method in ['PUT', 'PATCH', 'DELETE']:
            return True
        
        return False


class IsAuthenticated(permissions.BasePermission):
    message = "Требуется аутентификация."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
