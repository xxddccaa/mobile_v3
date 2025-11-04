from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import re

@dataclass
class InfoPool:
    """Keeping track of all information across the agents."""
    
    # User input / accumulated knowledge
    instruction: str = ""
    task_name: str = ""
    additional_knowledge_manager: str = ""
    additional_knowledge_executor: str = ""
    add_info_token = "[add_info]"
    
    ui_elements_list_before: str = "" # List of UI elements with index
    ui_elements_list_after: str = "" # List of UI elements with index
    action_pool: list = field(default_factory=list)

    # Working memory
    summary_history: list = field(default_factory=list)  # List of action descriptions
    action_history: list = field(default_factory=list)  # List of actions
    action_outcomes: list = field(default_factory=list)  # List of action outcomes
    error_descriptions: list = field(default_factory=list)

    last_summary: str = ""  # Last action description
    last_action: str = ""  # Last action
    last_action_thought: str = ""  # Last action thought
    important_notes: str = ""
    
    error_flag_plan: bool = False # if an error is not solved for multiple attempts with the executor
    error_description_plan: bool = False # explanation of the error for modifying the plan

    # Planning
    plan: str = ""
    completed_plan: str = ""
    progress_status: str = ""
    progress_status_history: list = field(default_factory=list)
    finish_thought: str = ""
    current_subgoal: str = ""
    # prev_subgoal: str = ""
    err_to_manager_thresh: int = 2

    # future tasks
    future_tasks: list = field(default_factory=list)

class BaseAgent(ABC):
    @abstractmethod
    def get_prompt(self, info_pool: InfoPool) -> str:
        pass
    @abstractmethod
    def parse_response(self, response: str) -> dict:
        pass

class Manager(BaseAgent):

    def get_prompt(self, info_pool: InfoPool) -> str:
        prompt = "你是一个能够代表用户操作安卓手机的智能代理。你的目标是跟踪进度并制定高层计划来实现用户的请求。\n\n"
        prompt += "### User Request ###\n"
        prompt += f"{info_pool.instruction}\n\n"

        task_specific_note = ""
        if ".html" in info_pool.instruction:
            task_specific_note = "注意：.html文件可能包含额外的可交互元素，例如绘图画布或游戏。在完成.html文件中的任务之前，不要打开其他应用。"
        elif "Audio Recorder" in info_pool.instruction:
            task_specific_note = "注意：停止录音图标是一个白色方块，位于底部从左数第四个位置。请不要点击中间的圆形暂停图标。"

        if info_pool.plan == "":
            # first time planning
            prompt += "---\n"
            prompt += "制定一个高层计划来实现用户的请求。如果请求比较复杂，请将其分解为子目标。截图显示了手机的初始状态。\n"
            prompt += "重要提示：对于明确要求回答的请求，始终要在计划的最后一步添加'执行answer动作'！\n\n"
            if task_specific_note != "":
                prompt += f"{task_specific_note}\n\n"
            
            prompt += "### Guidelines ###\n"
            prompt += "以下指导原则将帮助你规划此请求。\n"
            prompt += "通用原则：\n"
            prompt += "如果搜索功能适用，使用搜索快速找到具有特定名称的文件或条目。\n"
            prompt += "任务特定原则：\n"
            if info_pool.additional_knowledge_manager != "":
                prompt += f"{info_pool.additional_knowledge_manager}\n\n"
            else:
                prompt += f"{info_pool.add_info_token}\n\n"
            
            prompt += "请按以下格式提供你的输出，包含两个部分：\n"
            prompt += "### Thought ###\n"
            prompt += "详细解释你制定计划和子目标的理由。\n\n"
            prompt += "### Plan ###\n"
            prompt += "1. 第一个子目标\n"
            prompt += "2. 第二个子目标\n"
            prompt += "...\n"
        else:
            if info_pool.completed_plan != "No completed subgoal.":
                prompt += "### Historical Operations ###\n"
                prompt += "之前已完成的操作：\n"
                prompt += f"{info_pool.completed_plan}\n\n"
            prompt += "### Plan ###\n"
            prompt += f"{info_pool.plan}\n\n"
            prompt += f"### Last Action ###\n"
            prompt += f"{info_pool.last_action}\n\n"
            prompt += f"### Last Action Description ###\n"
            prompt += f"{info_pool.last_summary}\n\n"
            prompt += "### Important Notes ###\n"
            if info_pool.important_notes != "":
                prompt += f"{info_pool.important_notes}\n\n"
            else:
                prompt += "没有记录重要笔记。\n\n"
            prompt += "### Guidelines ###\n"
            prompt += "以下指导原则将帮助你规划此请求。\n"
            prompt += "通用原则：\n"
            prompt += "如果搜索功能适用，使用搜索快速找到具有特定名称的文件或条目。\n"
            prompt += "任务特定原则：\n"
            if info_pool.additional_knowledge_manager != "":
                prompt += f"{info_pool.additional_knowledge_manager}\n\n"
            else:
                prompt += f"{info_pool.add_info_token}\n\n"
            if info_pool.error_flag_plan:
                prompt += "### Potentially Stuck! ###\n"
                prompt += "你已经遇到了多次失败的尝试。以下是一些日志：\n"
                k = info_pool.err_to_manager_thresh
                recent_actions = info_pool.action_history[-k:]
                recent_summaries = info_pool.summary_history[-k:]
                recent_err_des = info_pool.error_descriptions[-k:]
                for i, (act, summ, err_des) in enumerate(zip(recent_actions, recent_summaries, recent_err_des)):
                    prompt += f"- 尝试：动作：{act} | 描述：{summ} | 结果：失败 | 反馈：{err_des}\n"

            prompt += "---\n"
            prompt += "仔细评估当前状态和提供的截图。检查当前计划是否需要修订。\n 判断用户请求是否已完全完成。如果你确信不再需要进一步的操作，请在输出中将计划标记为'Finished'。如果用户请求尚未完成，请更新计划。如果你遇到错误而陷入困境，请逐步思考是否需要修订整体计划以解决错误。\n"
            prompt += "注意：1. 如果当前情况阻止了原计划的进行或需要用户澄清，请做出合理的假设并相应地修订计划。在这种情况下，表现得就像你是用户一样。2. 请首先参考指导原则中的有用信息和步骤进行规划。3. 如果计划中的第一个子目标已经完成，请根据截图和进度及时更新计划，确保下一个子目标始终是计划中的第一项。4. 如果第一个子目标尚未完成，请复制上一轮的计划或根据子目标的完成情况更新计划。\n"
            prompt += "重要提示：如果接下来的步骤需要answer动作，请确保计划中包含执行answer动作的步骤。在这种情况下，除非最后一个动作是answer，否则不应将计划标记为'Finished'。\n"
            if task_specific_note != "":
              prompt += f"{task_specific_note}\n\n"

            prompt += "请按以下格式提供你的输出，包含三个部分：\n\n"
            prompt += "### Thought ###\n"
            prompt += "解释你对更新后的计划和当前子目标的理由。\n\n"
            prompt += "### Historical Operations ###\n"
            prompt += "尝试将最近完成的子目标添加到现有历史操作的顶部。请不要删除任何现有的历史操作。如果没有新完成的子目标，只需复制现有的历史操作。\n\n"
            prompt += "### Plan ###\n"
            prompt += "请根据当前页面和进度更新或复制现有计划。请密切关注历史操作。除非你能从屏幕状态判断某个子目标确实未完成，否则请不要重复已完成内容的计划。\n"
            
        return prompt

    def parse_response(self, response: str) -> dict:
        if "### Historical Operations" in response:
            thought = response.split("### Thought")[-1].split("### Historical Operations")[0].replace("\n", " ").replace("  ", " ").replace("###", "").strip()
            completed_subgoal = response.split("### Historical Operations")[-1].split("### Plan")[0].replace("\n", " ").replace("  ", " ").replace("###", "").strip()
        else:
            thought = response.split("### Thought")[-1].split("### Plan")[0].replace("\n", " ").replace("  ", " ").replace("###", "").strip()
            completed_subgoal = "No completed subgoal."
        plan = response.split("### Plan")[-1].replace("\n", " ").replace("  ", " ").replace("###", "").strip()
        return {"thought": thought, "completed_subgoal": completed_subgoal,  "plan": plan}

from utils.new_json_action import *

ATOMIC_ACTION_SIGNITURES_noxml = {
    ANSWER: {
        "arguments": ["text"],
        "description": lambda info: "回答用户的问题。使用示例：{\"action\": \"answer\", \"text\": \"你的答案内容\"}"
    },
    CLICK: {
        "arguments": ["coordinate"],
        "description": lambda info: "点击屏幕上指定(x, y)坐标的位置。使用示例：{\"action\": \"click\", \"coordinate\": [x, y]}"
    },
    LONG_PRESS: {
        "arguments": ["coordinate"],
        "description": lambda info: "长按屏幕上的(x, y)位置。使用示例：{\"action\": \"long_press\", \"coordinate\": [x, y]}"
    },
    TYPE: {
        "arguments": ["text"],
        "description": lambda info: "在当前激活的输入框或文本字段中输入文本。如果你已激活输入框，可以在屏幕底部看到\"ADB Keyboard {on}\"字样。如果没有，请再次点击输入框进行确认。在输入之前，请确保正确的输入框已被激活。使用示例：{\"action\": \"type\", \"text\": \"你想输入的文本\"}"
    },
    SYSTEM_BUTTON: {
        "arguments": ["button"],
        "description": lambda info: "按下系统按钮，包括返回(Back)、主页(Home)和回车(Enter)。使用示例：{\"action\": \"system_button\", \"button\": \"Home\"}"
    },
    SWIPE: {
        "arguments": ["coordinate", "coordinate2"],
        "description": lambda info: "从coordinate位置滑动到coordinate2位置。请确保滑动的起点和终点位于可滑动区域内，并远离键盘(y1 < 1400)。使用示例：{\"action\": \"swipe\", \"coordinate\": [x1, y1], \"coordinate2\": [x2, y2]}"
    },
    OPEN_APP: {
        "arguments": ["text"],
        "description": lambda info: "通过应用名称或包名直接打开应用。这比点击应用图标更快。支持中英文常见应用名称（例如，'微博'、'weibo'、'WeChat'、'微信'）。使用示例：{\"action\": \"open_app\", \"text\": \"微博\"}"
    },
    WAIT: {
        "arguments": ["time"],
        "description": lambda info: "等待指定的秒数。适用于等待页面加载、动画或网络请求完成。使用示例：{\"action\": \"wait\", \"time\": 3}"
    }
}

INPUT_KNOW = "如果你已激活了一个输入字段，你会在屏幕底部看到\"ADB Keyboard {on}\"。这款手机不显示软键盘。所以，如果你在屏幕底部看到\"ADB Keyboard {on}\"，就意味着你可以输入文本。否则，你需要点击正确的输入字段来激活它。"

class Executor(BaseAgent):

    def get_prompt(self, info_pool: InfoPool) -> str:
        prompt = "你是一个能够代表用户操作安卓手机的智能代理。你的目标是根据手机的当前状态和用户的请求来决定下一步要执行的动作。\n\n"

        prompt += "### User Request ###\n"
        prompt += f"{info_pool.instruction}\n\n"

        prompt += "### Overall Plan ###\n"
        prompt += f"{info_pool.plan}\n\n"
        
        prompt += "### Current Subgoal ###\n"
        current_goal = info_pool.plan
        current_goal = re.split(r'(?<=\d)\. ', current_goal)
        truncated_current_goal = ". ".join(current_goal[:4]) + '.'
        truncated_current_goal = truncated_current_goal[:-2].strip()
        prompt += f"{truncated_current_goal}\n\n"

        prompt += "### Progress Status ###\n"
        if info_pool.progress_status != "":
            prompt += f"{info_pool.progress_status}\n\n"
        else:
            prompt += "尚无进度。\n\n"

        if info_pool.additional_knowledge_executor != "":
            prompt += "### Guidelines ###\n"
            prompt += f"{info_pool.additional_knowledge_executor}\n"

        if "exact duplicates" in info_pool.instruction:
            prompt += "任务特定原则：\n只有具有相同名称、日期和详细信息的两个项目才能被视为重复项。\n\n"
        elif "Audio Recorder" in info_pool.instruction:
            prompt += "任务特定原则：\n停止录音图标是一个白色方块，位于底部从左数第四个位置。请不要点击中间的圆形暂停图标。\n\n"
        else:
            prompt += "\n"
        
        prompt += "---\n"        
        prompt += "仔细检查上面提供的所有信息，并决定要执行的下一个动作。如果你注意到上一个动作中存在未解决的错误，请像人类用户一样思考并尝试纠正它们。你必须从原子动作中选择你的动作。\n\n"
        
        prompt += "#### Atomic Actions ####\n"
        prompt += "原子动作函数以`动作(参数): 描述`的格式列出如下：\n"

        for action, value in ATOMIC_ACTION_SIGNITURES_noxml.items():
            prompt += f"- {action}({', '.join(value['arguments'])}): {value['description'](info_pool)}\n"

        prompt += "\n"
        prompt += "### Latest Action History ###\n"
        if info_pool.action_history != []:
            prompt += "你之前执行的最近动作以及它们是否成功：\n"
            num_actions = min(5, len(info_pool.action_history))
            latest_actions = info_pool.action_history[-num_actions:]
            latest_summary = info_pool.summary_history[-num_actions:]
            latest_outcomes = info_pool.action_outcomes[-num_actions:]
            error_descriptions = info_pool.error_descriptions[-num_actions:]
            action_log_strs = []
            for act, summ, outcome, err_des in zip(latest_actions, latest_summary, latest_outcomes, error_descriptions):
                if outcome == "A":
                    action_log_str = f"动作：{act} | 描述：{summ} | 结果：成功\n"
                else:
                    action_log_str = f"动作：{act} | 描述：{summ} | 结果：失败 | 反馈：{err_des}\n"
                prompt += action_log_str
                action_log_strs.append(action_log_str)
            
            prompt += "\n"
        else:
            prompt += "尚未执行任何动作。\n\n"

        prompt += "---\n"
        prompt += "重要提示：\n1. 不要多次重复之前失败的动作。尝试改变为另一个动作。\n"
        prompt += "2. 请优先考虑当前的子目标。\n\n"
        prompt += "请按以下格式提供你的输出，包含三个部分：\n"
        prompt += "### Thought ###\n"
        prompt += "详细解释你选择该动作的理由。\n\n"

        prompt += "### Action ###\n"
        prompt += "从提供的选项中只选择一个动作或快捷方式。\n"
        prompt += "你必须使用有效的JSON格式提供你的决定，指定`action`和动作的参数。例如，如果你想输入一些文本，你应该写{\"action\":\"type\", \"text\": \"你想输入的文本\"}。\n\n"
        
        prompt += "### Description ###\n"
        prompt += "对所选动作的简要描述。不要描述预期结果。\n"
        return prompt

    def parse_response(self, response: str) -> dict:
        thought = response.split("### Thought")[-1].split("### Action")[0].replace("\n", " ").replace("  ", " ").replace("###", "").strip()
        action = response.split("### Action")[-1].split("### Description")[0].replace("\n", " ").replace("  ", " ").replace("###", "").strip()
        description = response.split("### Description")[-1].replace("\n", " ").replace("  ", " ").replace("###", "").strip()
        return {"thought": thought, "action": action, "description": description}

class ActionReflector(BaseAgent):

    def get_prompt(self, info_pool: InfoPool) -> str:
        prompt = "你是一个能够代表用户操作安卓手机的智能代理。你的目标是验证上一个动作是否产生了预期的行为，并跟踪整体进度。\n\n"

        prompt += "### User Request ###\n"
        prompt += f"{info_pool.instruction}\n\n"
        
        prompt += "### Progress Status ###\n"
        if info_pool.completed_plan != "":
            prompt += f"{info_pool.completed_plan}\n\n"
        else:
            prompt += "尚无进度。\n\n"

        prompt += "---\n"
        prompt += "附加的两张图片是在你最后一个动作之前和之后拍摄的手机截图。\n"

        prompt += "---\n"
        prompt += "### Latest Action ###\n"
        prompt += f"动作：{info_pool.last_action}\n"
        prompt += f"预期：{info_pool.last_summary}\n\n"

        prompt += "---\n"
        prompt += "仔细检查上面提供的信息，以确定上一个动作是否产生了预期的行为。如果动作成功，请相应地更新进度状态。如果动作失败，请识别失败模式并提供导致此失败的潜在原因。\n\n"
        prompt += "注意：对于滑动以滚动屏幕查看更多内容，如果滑动前后显示的内容完全相同，则滑动被视为C：失败。上一个动作没有产生变化。这可能是因为内容已滚动到底部。\n\n"

        prompt += "请按以下格式提供你的输出，包含两个部分：\n"
        prompt += "### Outcome ###\n"
        prompt += "从以下选项中选择。将你的回答提供为\"A\"、\"B\"或\"C\"：\n"
        prompt += "A：成功或部分成功。上一个动作的结果符合预期。\n"
        prompt += "B：失败。上一个动作导致进入错误的页面。我需要返回到之前的状态。\n"
        prompt += "C：失败。上一个动作没有产生任何变化。\n\n"

        prompt += "### Error Description ###\n"
        prompt += "如果动作失败，请提供错误的详细描述以及导致此失败的潜在原因。如果动作成功，请在此处填写\"None\"。\n"

        return prompt

    def parse_response(self, response: str) -> dict:
        outcome = response.split("### Outcome")[-1].split("### Error Description")[0].replace("\n", " ").replace("  ", " ").replace("###", "").strip()
        error_description = response.split("### Error Description")[-1].replace("\n", " ").replace("###", "").replace("  ", " ").strip()
        return {"outcome": outcome, "error_description": error_description}

class Notetaker(BaseAgent):

    def get_prompt(self, info_pool: InfoPool) -> str:
        prompt = "你是一个帮助操作手机的AI助手。你的目标是记录与用户请求相关的重要内容。\n\n"

        prompt += "### User Request ###\n"
        prompt += f"{info_pool.instruction}\n\n"

        prompt += "### Progress Status ###\n"
        prompt += f"{info_pool.progress_status}\n\n"

        prompt += "### Existing Important Notes ###\n"
        if info_pool.important_notes != "":
            prompt += f"{info_pool.important_notes}\n\n"
        else:
            prompt += "没有记录重要笔记。\n\n"

        if "transactions" in info_pool.instruction and "Simple Gallery" in info_pool.instruction:
            prompt += "### Guideline ###\n你只能记录DCIM中的交易信息，因为其他交易与任务无关。\n"
        elif "enter their product" in info_pool.instruction:
            prompt += "### Guideline ###\n请记录每次出现的数字，以便你可以在最后计算它们的乘积。\n"
        
        prompt += "---\n"
        prompt += "仔细检查上面的信息，识别当前屏幕上需要记录的任何重要内容。\n"
        prompt += "重要提示：\n不要记录低级别的动作；只跟踪与用户请求相关的重要文本或视觉信息。不要重复用户请求或进度状态。不要编造你不确定的内容。\n\n"

        prompt += "请按以下格式提供你的输出：\n"
        prompt += "### Important Notes ###\n"
        prompt += "更新后的重要笔记，结合新旧笔记。如果没有新内容要记录，请复制现有的重要笔记。\n"

        return prompt

    def parse_response(self, response: str) -> dict:
        important_notes = response.split("### Important Notes")[-1].replace("\n", " ").replace("  ", " ").replace("###", "").strip()
        return {"important_notes": important_notes}