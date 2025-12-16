package second_in_command.skills.tactical

import com.fs.starfarer.api.combat.*
import com.fs.starfarer.api.input.InputEventAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.IntervalUtil
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class Superiority : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("+20%% 武器射程，若战场上存在友方空间站", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+10%% 武器射速，若战场上存在友方空间站", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())


    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

}

class SuperiorityListener(var owner: Int) : EveryFrameCombatPlugin {

    var interval = IntervalUtil(0.4f, 0.5f)

    override fun init(engine: CombatEngineAPI?) {

    }

    override fun processInputPreCoreControls(amount: Float, events: MutableList<InputEventAPI>?) {

    }

    override fun advance(amount: Float, events: MutableList<InputEventAPI>?) {
        interval.advance(amount)
        if (interval.intervalElapsed()) {

        }
    }

    override fun renderInWorldCoords(viewport: ViewportAPI?) {

    }

    override fun renderInUICoords(viewport: ViewportAPI?) {

    }

}