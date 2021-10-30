from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.http import HttpResponse
from dcodex.models import Manuscript
