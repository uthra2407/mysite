from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Question,Choice,Tag
from django.views.decorators.csrf import csrf_exempt
import json
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'
    def get_queryset(self):
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

@csrf_exempt
def poll(request, id=None):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Create a new Question object
        q = Question(question_text=data["Question"], pub_date=timezone.now())
        q.save()
        # Create Choices for the Question
        for option in data["OptionVote"]:
            q.choice_set.create(choice_text=option)
        # Add Tags to the Question
        for tag in data["Tags"]:
            t = Tag.objects.get_or_create(tag_text=tag)[0]
            q.tags.add(t)
        response = JsonResponse({"msg": "Inserted polls successfully"})
        response["Access-Control-Allow-Origin"] = "http://localhost:3000/createpoll/"  
        response["Access-Control-Allow-Methods"] = "GET, POST"
        return response
    
    
    #Fetch all polls
    elif request.method == 'GET':
        if id is not None:
            data = {}
            try:
                q = Question.objects.get(id=id)
                data["Question"] = q.question_text
                choice = {}
                for c in q.choice_set.all():
                    choice[c.choice_text] = c.votes
                data["OptionVote"] = choice
                data["QuestionId"] = id
                tags = []
    
                for tag in q.tags.all():
                    tags.append(tag.name)
                data["Tags"] = tags
                res = {"msg": "Fetched polls successfully", "data": data}
            except Question.DoesNotExist:
                res = {"msg": f"Question with id {id} not found"}
        
            return JsonResponse(res)
        
        # Filtered questions based on tags
        else:
            tags = request.GET.getlist('tags')  
            if tags:
               
                filtered_questions = Question.objects.filter(tags__tag_text__in=tags).distinct()
            else:
                filtered_questions = Question.objects.all()
            polls_data = []
            for question in filtered_questions:
                question_data = {
                    "Question": question.question_text,
                    "OptionVote": {choice.choice_text: choice.votes for choice in question.choice_set.all()},
                    "QuestionId": question.id,
                    "Tags": [tag.tag_text for tag in question.tags.all()]
                }
                polls_data.append(question_data)
        
            return JsonResponse({"msg": "Fetched polls successfully", "data": polls_data})
    
    else:
        return JsonResponse({"error": "Only GET, POST, and PUT requests are allowed"}, status=405)

@csrf_exempt
def update_vote(request, id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        increment_option = data.get("incrementOption")
        if increment_option:
            try:
                question = Question.objects.get(id=id)
                choice_to_increment = question.choice_set.get(choice_text=increment_option)
                choice_to_increment.votes += 1
                choice_to_increment.save()
                res = {"msg": "Poll vote updated successfully"}
            except (Question.DoesNotExist, Choice.DoesNotExist):
                res = {"msg": f"Question or choice with id {id} not found"}
        else:
            res = {"msg": "Please provide 'incrementOption' in the payload"}
        return JsonResponse(res)
    else:
        return JsonResponse({"msg": "Invalid request method"}, status=405)
    
@csrf_exempt
def all_poll(request, id):
    if request.method == 'GET':
        try:
            question = Question.objects.get(id=id)
            options = {}
            for choice in question.choice_set.all():
                options[choice.choice_text] = choice.votes
            
            tags = [tag.tag_text for tag in question.tags.all()]
            
            poll_details = {
                "Question": question.question_text,
                "OptionVote": options,
                "QuestionID": question.id,
                "Tags": tags
            }
            
            return JsonResponse({"msg": "Fetched poll details successfully", "data": poll_details})
        except Question.DoesNotExist:
            return JsonResponse({"error": f"Question with ID {id} not found"}, status=404)
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)
@csrf_exempt
def tags(request):
    tags = []
    for t in Tag.objects.all():
        tags.append(t.tag_text)
    res = {"Tags": tags}
    return JsonResponse(res)
@csrf_exempt
def delete(request, poll_id):
    if request.method == 'POST':
        poll = get_object_or_404(Question, id=poll_id)
        poll.delete()
        return JsonResponse({'status': 'success'})  # Return JSON response after deletion
    return JsonResponse({'error': 'Invalid request method'}, status=400)  # Return error for non-POST request
def delete_tag(request, tag_text):
    try:
        tag = Tag.objects.get(tag_text=tag_text)
        tag.delete()
        return JsonResponse({'status': 'success'})
    except Tag.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Tag not found'}, status=404)
