from django.contrib.contenttypes.models import ContentType


def get_permissions(request, objects):

    model = objects.model

    ct = ContentType.objects.get_for_model(model)

    app_label = ct.app_label
    model_name = ct.model

    permissions = {
        "add": request.user.has_perm(f"{app_label}.add_{model_name}"),
        "change": request.user.has_perm(f"{app_label}.change_{model_name}"),
        "delete": request.user.has_perm(f"{app_label}.delete_{model_name}"),
        "view": request.user.has_perm(f"{app_label}.view_{model_name}"),
    }

    return permissions
